import os
import uuid
import shutil
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from core.config import settings
from core.guardrails import EmotionalGuardrails
from core.gemini_client import gemini_multimodal_client
from database.connection import get_db, active_db_dialect
from database.repository import ChatRepository
from database.models import SessionModel
from rag.retriever import rag_retriever
from api.schemas import SessionCreate, SessionResponse, MessageResponse, ChatResponse, DocumentIngestRequest, DocumentResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")

# 1. Healthcheck
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database_dialect": active_db_dialect,
        "gemini_model": settings.GEMINI_MODEL,
        "gemini_api_configured": bool(settings.GEMINI_API_KEY)
    }

# 2. Session Management
@router.post("/sessions", response_model=SessionResponse)
def create_session(payload: Optional[SessionCreate] = None, db: Session = Depends(get_db)):
    title = payload.title if payload and payload.title else "New Conversation"
    session = ChatRepository.create_session(db, title=title)
    return session

@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    return ChatRepository.list_sessions(db)

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    session = ChatRepository.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return ChatRepository.get_session_messages(db, session_id)

# 3. Main Multimodal Chat Endpoint
@router.post("/chat", response_model=ChatResponse)
def chat_interaction(
    session_id: str = Form(...),
    message: Optional[str] = Form(None),
    enable_voice_output: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    audio: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Ensure session exists
    session = ChatRepository.get_or_create_session(db, session_id)
    
    user_prompt = (message or "").strip()
    saved_image_path = None
    saved_audio_path = None
    media_type = "none"
    media_url = None

    # Handle image upload
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1] or ".png"
        img_filename = f"img_{uuid.uuid4().hex[:8]}{ext}"
        dest_path = settings.IMAGE_DIR / img_filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        saved_image_path = str(dest_path)
        media_type = "image"
        media_url = f"/uploads/images/{img_filename}"

    # Handle audio upload
    if audio and audio.filename:
        ext = os.path.splitext(audio.filename)[1] or ".wav"
        aud_filename = f"aud_{uuid.uuid4().hex[:8]}{ext}"
        dest_path = settings.AUDIO_DIR / aud_filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        saved_audio_path = str(dest_path)
        media_type = "audio"
        media_url = f"/uploads/audio/{aud_filename}"

    # Validate that at least some input was provided
    if not user_prompt and not saved_image_path and not saved_audio_path:
        raise HTTPException(status_code=400, detail="Must provide at least a text message, image, or audio recording.")

    # 1. Evaluate Guardrails
    guardrail_decision = EmotionalGuardrails.evaluate_input(user_prompt)
    sanitized_prompt = guardrail_decision["sanitized_text"]

    # Record User Message in Database
    ChatRepository.add_message(
        db=db,
        session_id=session_id,
        sender_type="user",
        text_content=sanitized_prompt or "[Media Upload]",
        has_media=bool(saved_image_path or saved_audio_path),
        media_type=media_type,
        media_url=media_url,
        guardrail_flagged=guardrail_decision["blocked"]
    )

    # Automatically set session title if first message
    if session.session_title == "New Conversation" and user_prompt:
        clean_title = user_prompt[:40] + ("..." if len(user_prompt) > 40 else "")
        ChatRepository.update_session_title(db, session_id, clean_title)

    # If Guardrail Flagged (Crisis, Jailbreak, Medical request)
    if guardrail_decision["blocked"]:
        response_text = guardrail_decision["response"]
        
        # Optionally generate voice for crisis/block response
        audio_url = None
        if enable_voice_output:
            audio_url = gemini_multimodal_client.text_to_speech(response_text)

        # Record Guardrail Response in Database
        ChatRepository.add_message(
            db=db,
            session_id=session_id,
            sender_type="assistant",
            text_content=response_text,
            has_media=bool(audio_url),
            media_type="audio" if audio_url else "none",
            media_url=audio_url,
            guardrail_flagged=True
        )

        return ChatResponse(
            session_id=session_id,
            response_text=response_text,
            audio_output_url=audio_url,
            guardrail_flagged=True,
            guardrail_reason=guardrail_decision["reason"],
            retrieved_techniques=[],
            model_used="guardrail-safety-filter"
        )

    # 2. RAG Retrieval
    relevant_techniques = rag_retriever.retrieve(sanitized_prompt, top_k=2)
    rag_context = rag_retriever.format_context_for_prompt(relevant_techniques)

    # 3. Fetch recent history for conversation context
    past_messages = ChatRepository.get_session_messages(db, session_id)
    history_context = [
        {"sender": m.sender_type, "text": m.text_content or ""}
        for m in past_messages[-8:]
    ]

    # 4. Generate Gemini Multimodal Response
    gemini_result = gemini_multimodal_client.generate_multimodal_response(
        prompt=sanitized_prompt,
        image_path=saved_image_path,
        audio_path=saved_audio_path,
        rag_context=rag_context,
        chat_history=history_context
    )
    response_text = gemini_result["text"]

    # 5. Synthesize Voice Output (TTS) if enabled
    audio_output_url = None
    if enable_voice_output:
        audio_output_url = gemini_multimodal_client.text_to_speech(response_text)

    # 6. Save Assistant Response in Database
    ChatRepository.add_message(
        db=db,
        session_id=session_id,
        sender_type="assistant",
        text_content=response_text,
        has_media=bool(audio_output_url),
        media_type="audio" if audio_output_url else "none",
        media_url=audio_output_url,
        guardrail_flagged=False
    )

    return ChatResponse(
        session_id=session_id,
        response_text=response_text,
        audio_output_url=audio_output_url,
        guardrail_flagged=False,
        guardrail_reason=None,
        retrieved_techniques=relevant_techniques,
        model_used=gemini_result.get("model_used")
    )

# 4. Ingest Document into RAG & MySQL
@router.post("/rag/upload", response_model=DocumentResponse)
def ingest_document(payload: DocumentIngestRequest, db: Session = Depends(get_db)):
    doc = ChatRepository.add_document(
        db=db,
        title=payload.title,
        category=payload.category
    )
    
    # Split text into simple semantic paragraphs
    paragraphs = [p.strip() for p in payload.content.split("\n\n") if p.strip()]
    for idx, p in enumerate(paragraphs):
        ChatRepository.add_document_chunk(
            db=db,
            document_id=doc.document_id,
            chunk_text=p,
            chunk_index=idx
        )
        # Register dynamically in in-memory knowledge entries
        rag_retriever.knowledge_entries.append({
            "id": f"doc-{doc.document_id}-chunk-{idx}",
            "title": f"{payload.title} (Part {idx+1})",
            "category": payload.category,
            "triggers": [w.lower() for w in payload.title.split() if len(w) > 3],
            "content": p
        })

    return DocumentResponse(
        document_id=doc.document_id,
        title=doc.title,
        category=doc.category,
        chunks_created=len(paragraphs),
        created_at=doc.created_at
    )
