from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
from decimal import Decimal

class Lesson(BaseModel):
    id: str
    title: str
    subject: str
    grade_level: int

class LessonCompletion(BaseModel):
    id: Optional[str] = None
    student_id: str
    lesson_id: str
    completion_date: datetime
    score: float
    duration_minutes: int
    status: str  # 'completed', 'in_progress', 'failed'

    @validator('score')
    def validate_score(cls, v):
        # Convert float to string for DynamoDB compatibility
        return str(v)

    class Config:
        json_encoders = {
            str: lambda v: float(v) if v.replace('.', '').isdigit() else v
        } 