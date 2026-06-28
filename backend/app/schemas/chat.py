from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    role:    str
    content: str

class ChatRequest(BaseModel):
    question: str
    subject:  Optional[str] = None
    history:  List[ChatMessage] = []

class Source(BaseModel):
    filename: str
    page:     Optional[int] = None
    chunk_id: str = ""

class ChatResponse(BaseModel):
    answer:  str
    sources: List[Source] = []