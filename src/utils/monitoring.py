import boto3
from datetime import datetime
from fastapi import Request
from functools import wraps
import time
import os

def get_cloudwatch_client():
    """Get CloudWatch client with default region"""
    return boto3.client('cloudwatch', region_name='eu-west-1')

def monitor_endpoint(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            status = 'SUCCESS'
        except Exception as e:
            status = 'ERROR'
            raise e
        finally:
            execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Only send metrics if not in testing mode
            if not os.getenv('TESTING'):
                try:
                    cloudwatch = get_cloudwatch_client()
                    cloudwatch.put_metric_data(
                        Namespace='LessonCompletionAPI',
                        MetricData=[
                            {
                                'MetricName': 'EndpointLatency',
                                'Value': execution_time,
                                'Unit': 'Milliseconds',
                                'Dimensions': [
                                    {'Name': 'Endpoint', 'Value': func.__name__},
                                    {'Name': 'Status', 'Value': status}
                                ]
                            }
                        ]
                    )
                except Exception as e:
                    print(f"Failed to send metrics: {e}")
        
        return result
    return wrapper 