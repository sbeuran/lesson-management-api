from fastapi.testclient import TestClient
from datetime import datetime, timezone
import pytest
from src.api.routes import app
from src.models.lesson import LessonCompletion

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "message": "API and database are operational"
    }

def test_complete_lesson():
    completion_data = {
        "student_id": "test123",
        "lesson_id": "lesson456",
        "completed_at": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/lessons/complete", json=completion_data)
    assert response.status_code == 200
    assert "completion_id" in response.json()
    assert response.json()["message"] == "Lesson completion recorded"

def test_complete_lesson_invalid_data():
    # Missing required fields
    completion_data = {
        "student_id": "test123"
    }
    
    response = client.post("/lessons/complete", json=completion_data)
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()

def test_get_student_completions():
    # First create a completion
    completion_data = {
        "student_id": "test123",
        "lesson_id": "lesson456",
        "completed_at": datetime.now(timezone.utc).isoformat()
    }
    client.post("/lessons/complete", json=completion_data)
    
    # Then get completions
    response = client.get("/lessons/completions/test123")
    assert response.status_code == 200
    assert "completions" in response.json()
    completions = response.json()["completions"]
    assert len(completions) > 0
    assert completions[0]["student_id"] == "test123"
    assert completions[0]["lesson_id"] == "lesson456" 