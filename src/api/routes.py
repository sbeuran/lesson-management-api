from fastapi import FastAPI, HTTPException
from ..models.lesson import LessonCompletion
from ..services.dynamodb import DynamoDBService
from datetime import datetime
import uuid
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI()

# Initialize DynamoDB service
dynamodb = DynamoDBService()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    if not hasattr(app.state, 'dynamodb'):
        app.state.dynamodb = dynamodb

def get_dynamodb():
    """Get the DynamoDB service instance."""
    return app.state.dynamodb

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
        
        logger.info(f"Saving completion: {item}")
        
        # Save to DynamoDB using the shared service
        get_dynamodb().put_item(item)
        
        return {
            "message": "Lesson completion recorded",
            "completion_id": completion_id
        }
    except Exception as e:
        logger.error(f"Error in complete_lesson: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/completions/{student_id}")
async def get_student_completions(student_id: str):
    try:
        logger.info(f"Getting completions for student: {student_id}")
        # Query DynamoDB using the shared service
        completions = get_dynamodb().query_items(student_id)
        return {
            "student_id": student_id,
            "completions": completions
        }
    except Exception as e:
        logger.error(f"Error in get_student_completions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 