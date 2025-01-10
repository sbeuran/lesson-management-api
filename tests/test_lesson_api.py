import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from src.api.routes import app
from src.models.lesson import CompletionStatus
import boto3
import os
from moto import mock_dynamodb

client = TestClient(app)

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"

@pytest.fixture
def dynamodb(aws_credentials):
    """Create a mock DynamoDB."""
    with mock_dynamodb():
        # Create the DynamoDB table
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.create_table(
            TableName="lesson_completions",
            KeySchema=[
                {"AttributeName": "student_id", "KeyType": "HASH"},
                {"AttributeName": "id", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "student_id", "AttributeType": "S"},
                {"AttributeName": "id", "AttributeType": "S"}
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
        )
        table.meta.client.get_waiter("table_exists").wait(TableName="lesson_completions")
        yield dynamodb

@pytest.mark.usefixtures("dynamodb")
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

@pytest.mark.usefixtures("dynamodb")
def test_get_student_completions():
    # First create a completion
    completion_data = {
        "student_id": "test123",
        "lesson_id": "lesson456",
        "completion_date": datetime.now().isoformat(),
        "score": 95.5,
        "duration_minutes": 45,
        "status": CompletionStatus.COMPLETED.value
    }
    client.post("/lessons/completion", json=completion_data)
    
    # Then get the completions
    response = client.get(f"/lessons/completion/{completion_data['student_id']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy" 