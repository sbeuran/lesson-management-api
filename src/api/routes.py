from fastapi import FastAPI, HTTPException
from typing import List, Optional
from ..models.lesson import LessonCompletion
import boto3
from botocore.exceptions import ClientError
import logging
import json
from datetime import datetime
import uuid
import os

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI()

# Configure DynamoDB based on environment
def get_dynamodb_client():
    if os.getenv('TESTING') == 'true':
        return boto3.resource(
            'dynamodb',
            region_name='eu-west-1',
            aws_access_key_id='testing',
            aws_secret_access_key='testing'
        )
    return boto3.resource('dynamodb')

# Initialize DynamoDB table
table = None

def get_table():
    global table
    if table is None:
        table = get_dynamodb_client().Table('lesson_completions')
    return table

@app.get("/health")
async def health_check():
    try:
        # Test DynamoDB connection
        get_table().scan(Limit=1)
        return {"status": "healthy", "message": "API and database are operational"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.get("/lessons/completion")
async def list_completions() -> List[dict]:
    try:
        logger.info("Scanning DynamoDB table")
        response = get_table().scan()
        items = response.get('Items', [])
        logger.info(f"Found {len(items)} items")
        return items
    except ClientError as e:
        logger.error(f"DynamoDB error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/completion/{student_id}")
async def get_student_completions(student_id: str) -> List[dict]:
    try:
        logger.info(f"Querying completions for student: {student_id}")
        response = get_table().query(
            KeyConditionExpression='student_id = :sid',
            ExpressionAttributeValues={':sid': student_id}
        )
        items = response.get('Items', [])
        logger.info(f"Found {len(items)} items")
        return items
    except ClientError as e:
        logger.error(f"DynamoDB error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/lessons/completion")
async def create_completion(completion: LessonCompletion) -> dict:
    try:
        item = completion.model_dump()
        item['id'] = str(uuid.uuid4())
        
        logger.info(f"Creating completion: {json.dumps(item)}")
        get_table().put_item(Item=item)
        
        return {"message": "Completion created", "id": item['id']}
    except ClientError as e:
        logger.error(f"DynamoDB error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 