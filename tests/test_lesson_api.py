from fastapi.testclient import TestClient
from datetime import datetime, timezone
import pytest
import boto3
import os
from moto import mock_dynamodb
from src.api.routes import app
from src.models.lesson import LessonCompletion
from src.services.dynamodb import DynamoDBService
import logging

# Set up logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'
    os.environ['TESTING'] = 'true'

@pytest.fixture(scope="module")
def mock_dynamodb_service():
    """Create a mock DynamoDB service."""
    with mock_dynamodb():
        logger.info("Creating test DynamoDB table")
        dynamodb = boto3.resource('dynamodb')
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
        table.meta.client.get_waiter('table_exists').wait(TableName='lesson_completions')
        logger.info("Test DynamoDB table created")
        
        # Create and return the DynamoDB service
        service = DynamoDBService()
        yield service

@pytest.fixture(autouse=True)
def setup_app(mock_dynamodb_service):
    """Setup the FastAPI app with the mock DynamoDB service."""
    app.dependency_overrides = {}
    app.state.dynamodb = mock_dynamodb_service

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