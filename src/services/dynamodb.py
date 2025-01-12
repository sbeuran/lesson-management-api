import boto3
from botocore.exceptions import ClientError
import os

class DynamoDBService:
    def __init__(self):
        if os.getenv('TESTING') == 'true':
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url='http://localhost:5000'
            )
        else:
            self.dynamodb = boto3.resource('dynamodb')
        
        self.table = self.dynamodb.Table('lesson_completions')
    
    def put_item(self, item):
        try:
            response = self.table.put_item(Item=item)
            return response
        except ClientError as e:
            raise Exception(f"Failed to save completion: {str(e)}")
    
    def query_items(self, student_id):
        try:
            response = self.table.query(
                KeyConditionExpression='student_id = :sid',
                ExpressionAttributeValues={
                    ':sid': student_id
                }
            )
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Failed to query completions: {str(e)}") 