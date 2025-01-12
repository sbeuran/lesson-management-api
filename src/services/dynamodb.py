import boto3
from botocore.exceptions import ClientError
import os
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DynamoDBService:
    def __init__(self):
        if os.getenv('TESTING') == 'true':
            logger.info("Initializing DynamoDB in test mode")
            self.dynamodb = boto3.resource('dynamodb')
        else:
            logger.info("Initializing DynamoDB in production mode")
            self.dynamodb = boto3.resource('dynamodb')
        
        self.table = self.dynamodb.Table('lesson_completions')
        logger.info(f"DynamoDB table initialized: {self.table.table_name}")
    
    def put_item(self, item):
        try:
            logger.info(f"Putting item in DynamoDB: {item}")
            response = self.table.put_item(Item=item)
            logger.info(f"Put item response: {response}")
            return response
        except ClientError as e:
            logger.error(f"DynamoDB put_item error: {str(e)}", exc_info=True)
            raise Exception(f"Failed to save completion: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in put_item: {str(e)}", exc_info=True)
            raise
    
    def query_items(self, student_id):
        try:
            logger.info(f"Querying items for student_id: {student_id}")
            response = self.table.query(
                KeyConditionExpression='student_id = :sid',
                ExpressionAttributeValues={
                    ':sid': student_id
                }
            )
            items = response.get('Items', [])
            logger.info(f"Query returned {len(items)} items")
            return items
        except ClientError as e:
            logger.error(f"DynamoDB query error: {str(e)}", exc_info=True)
            raise Exception(f"Failed to query completions: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in query_items: {str(e)}", exc_info=True)
            raise 