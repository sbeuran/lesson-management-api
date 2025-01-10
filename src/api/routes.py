from fastapi import FastAPI, HTTPException, Path
from typing import List, Optional
from ..models.lesson import Lesson, LessonCompletion
from ..services.lesson_service import LessonService

app = FastAPI(title="Lesson Completion API")
lesson_service = LessonService()

@app.post("/lessons/completion", response_model=LessonCompletion)
async def record_lesson_completion(lesson_completion: LessonCompletion):
    """
    Record a new lesson completion for a student.
    """
    try:
        return await lesson_service.record_completion(lesson_completion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/completion/{student_id}", response_model=List[LessonCompletion])
async def get_student_completions(
    student_id: str = Path(..., description="The ID of the student to get completions for")
):
    """
    Get all lesson completions for a specific student.
    """
    try:
        completions = await lesson_service.get_student_completions(student_id)
        if not completions:
            raise HTTPException(status_code=404, detail=f"No completions found for student {student_id}")
        return completions
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint for the API.
    """
    return {"status": "healthy"} 