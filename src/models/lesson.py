from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class LessonCompletion(BaseModel):
    student_id: str = Field(..., min_length=1)
    lesson_id: str = Field(..., min_length=1)
    completion_date: datetime
    score: float = Field(..., ge=0, le=100)
    duration_minutes: int = Field(..., gt=0)
    status: Literal["completed", "in_progress", "failed"]

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 