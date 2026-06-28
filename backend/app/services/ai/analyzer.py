# Validated in Colab Notebook 6, Cell 2
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.quiz import QuizAttempt
from app.models.document import Document
from app.models.study_plan import StudyPlan
from typing import List, Dict

def get_weak_topics(user_id: int, db: Session, threshold: float = 60.0) -> List[Dict]:
    rows = (
        db.query(
            QuizAttempt.topic,
            QuizAttempt.subject,
            func.avg(QuizAttempt.score_percent).label("avg_score"),
            func.count(QuizAttempt.id).label("attempts"),
        )
        .filter(QuizAttempt.user_id == user_id)
        .group_by(QuizAttempt.topic, QuizAttempt.subject)
        .all()
    )
    results = []
    for row in rows:
        status = "weak" if row.avg_score < threshold else ("moderate" if row.avg_score < 75 else "strong")
        results.append({
            "topic":     row.topic,
            "subject":   row.subject,
            "avg_score": round(row.avg_score, 1),
            "attempts":  row.attempts,
            "status":    status,
        })
    return sorted(results, key=lambda x: x["avg_score"])

def get_dashboard_stats(user_id: int, db: Session) -> Dict:
    doc_count   = db.query(func.count(Document.id)).filter(Document.user_id == user_id).scalar() or 0
    quiz_count  = db.query(func.count(QuizAttempt.id)).filter(QuizAttempt.user_id == user_id).scalar() or 0
    avg_score   = db.query(func.avg(QuizAttempt.score_percent)).filter(QuizAttempt.user_id == user_id).scalar() or 0
    plan_count  = db.query(func.count(StudyPlan.id)).filter(StudyPlan.user_id == user_id).scalar() or 0
    recent      = (
        db.query(QuizAttempt)
        .filter(QuizAttempt.user_id == user_id)
        .order_by(QuizAttempt.attempted_at.desc())
        .limit(10).all()
    )
    return {
        "documents_uploaded":    doc_count,
        "quizzes_taken":         quiz_count,
        "average_score":         round(float(avg_score), 1),
        "study_plans_created":   plan_count,
        "recent_quizzes": [
            {"topic": q.topic, "score": q.score_percent, "date": str(q.attempted_at.date())}
            for q in recent
        ],
    }