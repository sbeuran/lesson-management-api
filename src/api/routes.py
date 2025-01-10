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
if os.getenv('TESTING') == 'true':
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='eu-west-1',
        aws_access_key_id='testing',
        aws_secret_access_key='testing'
    )
else:
    dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('lesson_completions')

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/lessons/completion")
async def list_completions() -> List[dict]:
    try:
        logger.info("Scanning DynamoDB table")
        response = table.scan()
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
        response = table.query(
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
        # Use model_dump() instead of dict() for Pydantic v2
        item = completion.model_dump()
        item['id'] = str(uuid.uuid4())
        
        logger.info(f"Creating completion: {json.dumps(item)}")
        table.put_item(Item=item)
        
        return {"message": "Completion created", "id": item['id']}
    except ClientError as e:
        logger.error(f"DynamoDB error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 