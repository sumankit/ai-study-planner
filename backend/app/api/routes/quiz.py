from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.quiz import QuizAttempt
from app.schemas.quiz import QuizRequest, QuizResponse, QuizSubmit, QuizResult
from app.services.ai.quiz_generator import generate_quiz

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.post("/generate", response_model=QuizResponse)
def generate(payload: QuizRequest, user: User = Depends(get_current_user)):
    try:
        questions = generate_quiz(user.id, payload.topic, payload.num_questions,
                                  payload.difficulty, payload.subject)
        return QuizResponse(topic=payload.topic, difficulty=payload.difficulty, questions=questions)
    except (ValueError, Exception) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/submit", response_model=QuizResult)
def submit(payload: QuizSubmit, db: Session = Depends(get_db),
           user: User = Depends(get_current_user)):
    total   = len(payload.questions_data)
    correct = sum(
        1 for q in payload.questions_data
        if payload.answers.get(str(q["id"])) == q["correct_answer"]
    )
    score   = round(correct / total * 100, 1) if total > 0 else 0
    attempt = QuizAttempt(
        user_id=user.id, topic=payload.topic, subject=payload.subject,
        difficulty=payload.difficulty, total_questions=total,
        correct_answers=correct, score_percent=score,
        questions_data=payload.questions_data,
    )
    db.add(attempt); db.commit(); db.refresh(attempt)
    return attempt

@router.get("/history", response_model=List[QuizResult])
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(QuizAttempt).filter(QuizAttempt.user_id == user.id)\
        .order_by(QuizAttempt.attempted_at.desc()).limit(20).all()