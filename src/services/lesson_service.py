import boto3
import uuid
from datetime import datetime
from typing import List
from ..models.lesson import LessonCompletion

class LessonService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table('lesson_completions')
        
    async def record_completion(self, completion: LessonCompletion) -> LessonCompletion:
        if not completion.id:
            completion.id = str(uuid.uuid4())
        
        item = completion.dict()
        item['completion_date'] = completion.completion_date.isoformat()
        
        self.table.put_item(Item=item)
        return completion
    
    async def get_student_completions(self, student_id: str) -> List[LessonCompletion]:
        response = self.table.query(
            KeyConditionExpression='student_id = :sid',
            ExpressionAttributeValues={':sid': student_id}
        )
        
        completions = []
        for item in response['Items']:
            item['completion_date'] = datetime.fromisoformat(item['completion_date'])
            completions.append(LessonCompletion(**item))
            
        return completions 