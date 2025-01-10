import boto3
import uuid
from datetime import datetime
from typing import List
from ..models.lesson import LessonCompletion

class LessonService:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
        self.table = self.dynamodb.Table('lesson_completions')
        
    async def record_completion(self, completion: LessonCompletion) -> LessonCompletion:
        try:
            if not completion.id:
                completion.id = str(uuid.uuid4())
            
            item = completion.dict()
            item['completion_date'] = completion.completion_date.isoformat()
            
            # Store the item in DynamoDB
            self.table.put_item(Item=item)
            
            # Convert score back to float for response
            if isinstance(item['score'], str):
                item['score'] = float(item['score'])
            
            return LessonCompletion(**item)
        except Exception as e:
            print(f"Error recording completion: {e}")
            raise
    
    async def get_student_completions(self, student_id: str) -> List[LessonCompletion]:
        try:
            response = self.table.query(
                KeyConditionExpression='student_id = :sid',
                ExpressionAttributeValues={':sid': student_id}
            )
            
            completions = []
            for item in response.get('Items', []):
                # Convert score back to float
                if isinstance(item['score'], str):
                    item['score'] = float(item['score'])
                item['completion_date'] = datetime.fromisoformat(item['completion_date'])
                completions.append(LessonCompletion(**item))
                
            return completions
        except Exception as e:
            print(f"Error getting completions: {e}")
            raise 