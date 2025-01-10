from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional
from decimal import Decimal

class CompletionStatus(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"

class LessonCompletion(BaseModel):
    student_id: str = Field(..., description="Student's unique identifier")
    lesson_id: str = Field(..., description="Lesson's unique identifier")
    completion_date: datetime = Field(default_factory=datetime.now)
    score: Decimal = Field(..., description="Lesson score")
    duration_minutes: int = Field(..., description="Duration in minutes")
    status: CompletionStatus = Field(..., description="Completion status")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: str
        }
        
    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # Convert datetime to string
        if isinstance(data['completion_date'], datetime):
            data['completion_date'] = data['completion_date'].isoformat()
        # Convert Decimal to string
        if isinstance(data['score'], Decimal):
            data['score'] = str(data['score'])
        return data 