from mangum import Mangum
from .routes import app, dynamodb
import json
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize app state
app.state.dynamodb = dynamodb

# Create Mangum handler for Lambda
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    try:
        # Log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle health check
        if '/health' in event.get('path', '') or '/health' in event.get('resource', ''):
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat()
                })
            }

        # Process request through Mangum
        try:
            response = handler(event, context)
            logger.info(f"Handler response: {json.dumps(response)}")
            return response
        except Exception as e:
            logger.error(f"Handler error: {str(e)}")
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "error": str(e)
                })
            }

    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": str(e)
            })
        } 