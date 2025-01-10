import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.api.routes import app
from src.models.lesson import LessonCompletion

client = TestClient(app)

def test_record_completion(dynamodb):
    completion_data = {
        "student_id": "test123",
        "lesson_id": "lesson456",
        "completion_date": datetime.now().isoformat(),
        "score": 95.5,
        "duration_minutes": 45,
        "status": "completed"
    }
    
    response = client.post("/lessons/completion", json=completion_data)
    assert response.status_code == 200
    assert response.json()["student_id"] == completion_data["student_id"]
    assert float(response.json()["score"]) == completion_data["score"]

def test_get_student_completions(dynamodb):
    # First create a completion
    completion_data = {
        "student_id": "test123",
        "lesson_id": "lesson456",
        "completion_date": datetime.now().isoformat(),
        "score": 95.5,
        "duration_minutes": 45,
        "status": "completed"
    }
    client.post("/lessons/completion", json=completion_data)
    
    # Then try to retrieve it
    response = client.get("/lessons/completion/test123")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0 