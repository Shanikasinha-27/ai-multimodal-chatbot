from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Enum
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class SessionModel(Base):
    __tablename__ = "sessions"

    session_id = Column(String(64), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    session_title = Column(String(255), default="New Conversation")

    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan")


class MessageModel(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id", ondelete="CASCADE"), nullable=False)
    sender_type = Column(Enum("user", "assistant", "system", name="sender_enum"), nullable=False)
    text_content = Column(Text, nullable=True)
    has_media = Column(Boolean, default=False)
    media_type = Column(Enum("image", "audio", "document", "none", name="media_type_enum"), default="none")
    media_url = Column(String(512), nullable=True)
    guardrail_flagged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("SessionModel", back_populates="messages")


class DocumentModel(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    category = Column(
        Enum("cbt", "mindfulness", "grounding", "general_support", name="category_enum"),
        nullable=False,
        default="general_support"
    )
    file_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunkModel", back_populates="document", cascade="all, delete-orphan")


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    chunk_id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    embedding_id = Column(String(128), nullable=True)

    document = relationship("DocumentModel", back_populates="chunks")
