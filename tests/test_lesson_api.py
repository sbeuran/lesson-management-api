import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.api.routes import app
from src.models.lesson import CompletionStatus

client = TestClient(app)

def test_record_completion():
    completion_data = {
        "student_id": "test123",
        "lesson_id": "lesson456",
        "completion_date": datetime.now().isoformat(),
        "score": 95.5,
        "duration_minutes": 45,
        "status": CompletionStatus.COMPLETED.value
    }
    
    response = client.post("/lessons/completion", json=completion_data)
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == completion_data["student_id"]
    assert data["lesson_id"] == completion_data["lesson_id"]

def test_get_student_completions():
    student_id = "test123"
    response = client.get(f"/lessons/completion/{student_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy" 