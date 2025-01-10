import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.api.routes import app
from src.models.lesson import LessonCompletion
import os
import boto3

# Ensure we're in testing mode
os.environ['TESTING'] = 'true'

client = TestClient(app)

@pytest.fixture(autouse=True)  # autouse=True makes this fixture run automatically
def mock_dynamodb(monkeypatch):
    """Mock DynamoDB interactions for testing"""
    class MockTable:
        def __init__(self):
            self.items = {}
        
        def put_item(self, Item):
            student_id = Item['student_id']
            self.items[student_id] = Item
            return {}
            
        def query(self, KeyConditionExpression, ExpressionAttributeValues):
            student_id = ExpressionAttributeValues[':sid']
            items = [self.items[student_id]] if student_id in self.items else []
            return {"Items": items}
    
    class MockDynamoDB:
        def __init__(self):
            self.table = MockTable()
            
        def Table(self, name):
            return self.table
    
    mock_db = MockDynamoDB()
    
    def mock_resource(*args, **kwargs):
        return mock_db
    
    # Mock both the resource and client
    monkeypatch.setattr(boto3, "resource", mock_resource)
    monkeypatch.setattr(boto3, "client", mock_resource)
    
    return mock_db

def test_record_completion():
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

def test_get_student_completions():
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