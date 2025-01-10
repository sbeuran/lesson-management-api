import sys
import os
import pytest
import boto3
from moto import mock_dynamodb

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set testing environment variables
os.environ['TESTING'] = 'true'
os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'

@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

@pytest.fixture(scope='function')
def dynamodb(aws_credentials):
    with mock_dynamodb():
        # Create the DynamoDB table
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
        
        yield table 