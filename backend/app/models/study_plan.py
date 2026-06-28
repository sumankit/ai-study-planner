from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class StudyPlan(Base):
    __tablename__ = "study_plans"
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    title       = Column(String, nullable=False)
    exam_date   = Column(Date,   nullable=False)
    daily_hours = Column(Integer, default=3)
    subjects    = Column(JSON,   nullable=True)
    schedule    = Column(JSON,   nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="study_plans")