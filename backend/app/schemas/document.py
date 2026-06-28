from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.document import DocumentType, ProcessingStatus

class DocumentOut(BaseModel):
    id:                int
    filename:          str
    original_filename: str
    file_type:         DocumentType
    subject:           Optional[str]
    status:            ProcessingStatus
    chunk_count:       int
    created_at:        datetime
    class Config:
        from_attributes = True