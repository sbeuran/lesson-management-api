from fastapi import FastAPI, HTTPException
from ..models.lesson import LessonCompletion
from ..services.dynamodb import DynamoDBService
from datetime import datetime
import uuid

app = FastAPI()
dynamodb = DynamoDBService()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "API and database are operational"
    }

@app.post("/lessons/complete")
async def complete_lesson(completion: LessonCompletion):
    try:
        # Generate unique ID for the completion
        completion_id = str(uuid.uuid4())
        
        # Create item for DynamoDB
        item = {
            'id': completion_id,
            'student_id': completion.student_id,
            'lesson_id': completion.lesson_id,
            'completed_at': completion.completed_at.isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Save to DynamoDB
        dynamodb.put_item(item)
        
        return {
            "message": "Lesson completion recorded",
            "completion_id": completion_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/completions/{student_id}")
async def get_student_completions(student_id: str):
    try:
        # Query DynamoDB for student's completions
        completions = dynamodb.query_items(student_id)
        return {
            "student_id": student_id,
            "completions": completions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 