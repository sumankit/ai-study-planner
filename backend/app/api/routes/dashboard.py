from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.ai.analyzer import get_weak_topics, get_dashboard_stats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/stats")
def stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_dashboard_stats(user.id, db)

@router.get("/weak-topics")
def weak(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_weak_topics(user.id, db)