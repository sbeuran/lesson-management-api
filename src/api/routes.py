from fastapi import FastAPI, HTTPException
from typing import List
from ..models.lesson import LessonCompletion
import boto3
import uuid
from datetime import datetime
import json
import os
from decimal import Decimal
import logging

app = FastAPI()

# Configure DynamoDB resource based on environment
if os.getenv('TESTING') == 'true':
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='eu-west-1',
        aws_access_key_id='testing',
        aws_secret_access_key='testing',
        endpoint_url=None  # Remove localhost endpoint
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
        item = completion.model_dump()
        item['id'] = completion_id
        
        # Convert datetime to string for DynamoDB
        if isinstance(item['completion_date'], datetime):
            item['completion_date'] = item['completion_date'].isoformat()
        
        # Ensure score is Decimal
        if isinstance(item['score'], float):
            item['score'] = Decimal(str(item['score']))
        
        table.put_item(Item=item)
        
        # Convert Decimal back to float for response
        item['score'] = float(item['score'])
        return item
    except Exception as e:
        logger.error(f"Error recording completion: {str(e)}", exc_info=True)
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
        items = response.get('Items', [])
        # Convert DynamoDB types to Python types
        for item in items:
            if 'score' in item:
                item['score'] = float(item['score'])
        return items
    except Exception as e:
        logger.error(f"Error listing completions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 