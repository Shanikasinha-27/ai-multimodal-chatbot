from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Session Schemas
class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class SessionResponse(BaseModel):
    session_id: str
    session_title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Message Schemas
class MessageResponse(BaseModel):
    message_id: int
    session_id: str
    sender_type: str
    text_content: Optional[str]
    has_media: bool
    media_type: str
    media_url: Optional[str]
    guardrail_flagged: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Multimodal Chat Response
class ChatResponse(BaseModel):
    session_id: str
    response_text: str
    audio_output_url: Optional[str] = None
    guardrail_flagged: bool = False
    guardrail_reason: Optional[str] = None
    retrieved_techniques: List[Dict[str, Any]] = Field(default_factory=list)
    model_used: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# RAG Ingest Schemas
class DocumentIngestRequest(BaseModel):
    title: str
    category: str = "general_support"
    content: str

class DocumentResponse(BaseModel):
    document_id: int
    title: str
    category: str
    chunks_created: int
    created_at: datetime
