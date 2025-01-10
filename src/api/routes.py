from fastapi import FastAPI, HTTPException
from typing import List, Optional
from ..models.lesson import Lesson, LessonCompletion
from ..services.lesson_service import LessonService
from ..utils.monitoring import monitor_endpoint

app = FastAPI(title="Lesson Completion API")
lesson_service = LessonService()

@app.post("/lessons/completion", response_model=LessonCompletion)
@monitor_endpoint
async def record_lesson_completion(lesson_completion: LessonCompletion):
    try:
        return await lesson_service.record_completion(lesson_completion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/completion/{student_id}", response_model=List[LessonCompletion])
@monitor_endpoint
async def get_student_completions(student_id: str):
    try:
        return await lesson_service.get_student_completions(student_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e)) 