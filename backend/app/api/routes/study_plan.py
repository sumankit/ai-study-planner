from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.study_plan import StudyPlan
from app.schemas.study_plan import StudyPlanRequest, StudyPlanOut
from app.services.ai.planner import generate_study_plan
from app.services.ai.analyzer import get_weak_topics

router = APIRouter(prefix="/study-plan", tags=["study-plan"])

@router.post("/generate", response_model=StudyPlanOut)
def generate(payload: StudyPlanRequest, db: Session = Depends(get_db),
             user: User = Depends(get_current_user)):
    weak   = get_weak_topics(user.id, db)
    w_names = [t["topic"] for t in weak if t["status"] == "weak"]
    try:
        schedule = generate_study_plan(payload.exam_date, payload.daily_hours,
                                       payload.subjects, w_names)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    plan = StudyPlan(user_id=user.id, title=payload.title, exam_date=payload.exam_date,
                     daily_hours=payload.daily_hours, subjects=payload.subjects, schedule=schedule)
    db.add(plan); db.commit(); db.refresh(plan)
    return plan

@router.get("/", response_model=List[StudyPlanOut])
def list_plans(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(StudyPlan).filter(StudyPlan.user_id == user.id)\
        .order_by(StudyPlan.created_at.desc()).all()