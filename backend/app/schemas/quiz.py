from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuizRequest(BaseModel):
    topic:         str
    subject:       Optional[str] = None
    num_questions: int  = 5
    difficulty:    str  = "medium"

class QuizOption(BaseModel):
    key:  str
    text: str

class QuizQuestion(BaseModel):
    id:             int
    question:       str
    options:        List[QuizOption]
    correct_answer: str
    explanation:    str

class QuizResponse(BaseModel):
    topic:      str
    difficulty: str
    questions:  List[QuizQuestion]

class QuizSubmit(BaseModel):
    topic:          str
    subject:        Optional[str] = None
    difficulty:     str
    answers:        dict
    questions_data: List[dict]

class QuizResult(BaseModel):
    id:              int
    score_percent:   float
    correct_answers: int
    total_questions: int
    topic:           str
    attempted_at:    datetime
    class Config:
        from_attributes = True