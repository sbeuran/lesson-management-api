import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.api.routes import app
from src.models.lesson import LessonCompletion
import os

# Ensure we're in testing mode
os.environ['TESTING'] = 'true'

client = TestClient(app)

@pytest.fixture
def mock_dynamodb(monkeypatch):
    """Mock DynamoDB interactions for testing"""
    class MockTable:
        def put_item(self, Item):
            return {}
            
        def query(self, KeyConditionExpression, ExpressionAttributeValues):
            return {"Items": []}
    
    class MockDynamoDB:
        def Table(self, name):
            return MockTable()
    
    def mock_resource(*args, **kwargs):
        return MockDynamoDB()
    
    import boto3
    monkeypatch.setattr(boto3, "resource", mock_resource)

def test_record_completion(mock_dynamodb):
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

def test_get_student_completions(mock_dynamodb):
    response = client.get("/lessons/completion/test123")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 