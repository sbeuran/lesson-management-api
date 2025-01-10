from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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