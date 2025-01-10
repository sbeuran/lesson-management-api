from fastapi.testclient import TestClient
from datetime import datetime
from src.api.routes import app
from src.models.lesson import CompletionStatus
from decimal import Decimal
import os
import pytest

# Set testing environment
os.environ['TESTING'] = 'true'

client = TestClient(app)

def test_health_check(dynamodb):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "API and database are operational"}

def test_record_completion(dynamodb):
    completion_data = {
        "student_id": "test123",
        "lesson_id": "lesson456",
        "completion_date": datetime.now().isoformat(),
        "score": str(Decimal('95.5')),
        "duration_minutes": 45,
        "status": CompletionStatus.COMPLETED.value
    }
    
    response = client.post("/lessons/completion", json=completion_data)
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_student_completions(dynamodb):
    # First create a completion
    completion_data = {
        "student_id": "test123",
        "lesson_id": "lesson456",
        "completion_date": datetime.now().isoformat(),
        "score": str(Decimal('95.5')),
        "duration_minutes": 45,
        "status": CompletionStatus.COMPLETED.value
    }
    client.post("/lessons/completion", json=completion_data)
    
    # Then get the completions
    response = client.get(f"/lessons/completion/{completion_data['student_id']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0 