import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models import SessionModel, MessageModel, DocumentModel, DocumentChunkModel

class ChatRepository:
    """Repository handling all database operations for sessions and messages."""

    @staticmethod
    def create_session(db: Session, session_id: Optional[str] = None, title: str = "New Conversation") -> SessionModel:
        sid = session_id or str(uuid.uuid4())
        session = SessionModel(session_id=sid, session_title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[SessionModel]:
        return db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

    @staticmethod
    def get_or_create_session(db: Session, session_id: Optional[str] = None) -> SessionModel:
        if session_id:
            existing = ChatRepository.get_session(db, session_id)
            if existing:
                return existing
        return ChatRepository.create_session(db, session_id=session_id)

    @staticmethod
    def list_sessions(db: Session, limit: int = 50) -> List[SessionModel]:
        return db.query(SessionModel).order_by(SessionModel.updated_at.desc()).limit(limit).all()

    @staticmethod
    def update_session_title(db: Session, session_id: str, title: str) -> Optional[SessionModel]:
        session = ChatRepository.get_session(db, session_id)
        if session:
            session.session_title = title[:250]
            db.commit()
            db.refresh(session)
        return session

    @staticmethod
    def add_message(
        db: Session,
        session_id: str,
        sender_type: str,
        text_content: Optional[str] = None,
        has_media: bool = False,
        media_type: str = "none",
        media_url: Optional[str] = None,
        guardrail_flagged: bool = False
    ) -> MessageModel:
        # Ensure session exists
        ChatRepository.get_or_create_session(db, session_id)
        
        msg = MessageModel(
            session_id=session_id,
            sender_type=sender_type,
            text_content=text_content,
            has_media=has_media,
            media_type=media_type,
            media_url=media_url,
            guardrail_flagged=guardrail_flagged
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    @staticmethod
    def get_session_messages(db: Session, session_id: str) -> List[MessageModel]:
        return (
            db.query(MessageModel)
            .filter(MessageModel.session_id == session_id)
            .order_by(MessageModel.created_at.asc())
            .all()
        )

    @staticmethod
    def add_document(db: Session, title: str, category: str = "general_support", file_path: Optional[str] = None) -> DocumentModel:
        doc = DocumentModel(title=title, category=category, file_path=file_path)
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    @staticmethod
    def add_document_chunk(
        db: Session,
        document_id: int,
        chunk_text: str,
        chunk_index: int,
        embedding_id: Optional[str] = None
    ) -> DocumentChunkModel:
        chunk = DocumentChunkModel(
            document_id=document_id,
            chunk_text=chunk_text,
            chunk_index=chunk_index,
            embedding_id=embedding_id
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def get_all_chunks(db: Session) -> List[DocumentChunkModel]:
        return db.query(DocumentChunkModel).all()
