from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base

class DocumentType(str, enum.Enum):
    PDF            = "pdf"
    PPT            = "ppt"
    SYLLABUS       = "syllabus"
    QUESTION_PAPER = "question_paper"

class ProcessingStatus(str, enum.Enum):
    PENDING    = "pending"
    PROCESSING = "processing"
    COMPLETED  = "completed"
    FAILED     = "failed"

class Document(Base):
    __tablename__ = "documents"
    id                = Column(Integer, primary_key=True, index=True)
    user_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename          = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_type         = Column(Enum(DocumentType), nullable=False)
    subject           = Column(String, nullable=True)
    file_path         = Column(String, nullable=False)
    status            = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)
    chunk_count       = Column(Integer, default=0)
    error_message     = Column(Text, nullable=True)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="documents")