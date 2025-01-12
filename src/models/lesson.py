from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LessonCompletion(BaseModel):
    student_id: str
    lesson_id: str
    completed_at: datetime 