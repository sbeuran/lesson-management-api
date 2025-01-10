from fastapi import FastAPI, HTTPException
from typing import List
from ..models.lesson import LessonCompletion
import boto3
import uuid
from datetime import datetime
import json
import os

app = FastAPI()

# Configure DynamoDB resource based on environment
if os.getenv('TESTING') == 'true':
    dynamodb = boto3.resource('dynamodb',
        aws_access_key_id='testing',
        aws_secret_access_key='testing',
        region_name='eu-west-1',
        endpoint_url='http://localhost:8000'
    )
else:
    dynamodb = boto3.resource('dynamodb')

table = dynamodb.Table('lesson_completions')

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/lessons/completion")
def record_completion(completion: LessonCompletion):
    try:
        completion_id = str(uuid.uuid4())
        item = completion.dict()
        item['id'] = completion_id
        
        # Convert datetime to string for DynamoDB
        if isinstance(item['completion_date'], datetime):
            item['completion_date'] = item['completion_date'].isoformat()
        
        table.put_item(Item=item)
        return item
    except Exception as e:
        print(f"Error recording completion: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/completion/{student_id}")
def get_student_completions(student_id: str) -> List[dict]:
    try:
        response = table.query(
            KeyConditionExpression='student_id = :sid',
            ExpressionAttributeValues={
                ':sid': student_id
            }
        )
        return response.get('Items', [])
    except Exception as e:
        print(f"Error getting completions: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/completion")
def list_completions() -> List[dict]:
    try:
        response = table.scan()
        return response.get('Items', [])
    except Exception as e:
        print(f"Error listing completions: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=str(e)) 