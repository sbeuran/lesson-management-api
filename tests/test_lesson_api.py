import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.api.routes import app
from src.models.lesson import LessonCompletion
import os
import boto3
from moto import mock_dynamodb, mock_cloudwatch

# Ensure we're in testing mode
os.environ['TESTING'] = 'true'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'

client = TestClient(app)

@pytest.fixture(autouse=True)
@mock_dynamodb
@mock_cloudwatch
def mock_aws():
    """Set up mock AWS services"""
    # Create DynamoDB table
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    
    # Create the table
    table = dynamodb.create_table(
        TableName='lesson_completions',
        KeySchema=[
            {'AttributeName': 'student_id', 'KeyType': 'HASH'},
            {'AttributeName': 'id', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'student_id', 'AttributeType': 'S'},
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    
    return table

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
    assert float(response.json()["score"]) == completion_data["score"]

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