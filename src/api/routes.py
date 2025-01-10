from fastapi import FastAPI, HTTPException
from typing import List
from ..models.lesson import LessonCompletion
import boto3
import uuid
from datetime import datetime
import json

app = FastAPI()
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('lesson_completions')

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/lessons/completion")
def record_completion(completion: LessonCompletion):
    try:
        completion_id = str(uuid.uuid4())
        item = completion.dict()
        item['id'] = completion_id
        
        table.put_item(Item=item)
        return item
    except Exception as e:
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/lessons/completion")
def list_completions() -> List[dict]:
    try:
        response = table.scan()
        return response.get('Items', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 