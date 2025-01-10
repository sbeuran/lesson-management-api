from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class CompletionStatus(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"

class LessonCompletion(BaseModel):
    student_id: str = Field(..., min_length=1)
    lesson_id: str = Field(..., min_length=1)
    completion_date: datetime
    score: float = Field(..., ge=0, le=100)
    duration_minutes: int = Field(..., gt=0)
    status: CompletionStatus

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 