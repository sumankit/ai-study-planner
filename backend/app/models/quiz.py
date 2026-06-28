from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic           = Column(String, nullable=False)
    subject         = Column(String, nullable=True)
    difficulty      = Column(String, default="medium")
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, default=0)
    score_percent   = Column(Float,   default=0.0)
    questions_data  = Column(JSON,    nullable=True)
    attempted_at    = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="quiz_attempts")