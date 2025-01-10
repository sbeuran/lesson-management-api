import pytest
import boto3
import os
from moto import mock_dynamodb

@pytest.fixture(autouse=True)
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-1"
    os.environ["TESTING"] = "true"

@pytest.fixture(autouse=True)
def dynamodb(aws_credentials):
    """Create a mock DynamoDB."""
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb',
            aws_access_key_id='testing',
            aws_secret_access_key='testing',
            region_name='eu-west-1'
        )
        
        # Create the DynamoDB table
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
        
        # Wait for table to be created
        table.meta.client.get_waiter("table_exists").wait(TableName="lesson_completions")
        yield dynamodb 