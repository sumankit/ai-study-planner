from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class StudyPlanRequest(BaseModel):
    title:       str
    exam_date:   date
    daily_hours: int = 3
    subjects:    List[str]

class StudyPlanOut(BaseModel):
    id:          int
    title:       str
    exam_date:   date
    daily_hours: int
    subjects:    Optional[List[str]]
    schedule:    Optional[dict]
    class Config:
        from_attributes = True