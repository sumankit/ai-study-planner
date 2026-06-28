from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai.rag_pipeline import rag_query

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db),
         user: User = Depends(get_current_user)):
    result = rag_query(user.id, payload.question, payload.history, payload.subject)
    return ChatResponse(**result)