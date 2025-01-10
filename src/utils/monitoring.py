import boto3
from datetime import datetime
from fastapi import Request
from functools import wraps
import time

cloudwatch = boto3.client('cloudwatch')

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
            
            # Send metrics to CloudWatch
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
        
        return result
    return wrapper 