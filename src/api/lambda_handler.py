from mangum import Mangum
from .routes import app
import json
import logging
from decimal import Decimal
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create Mangum handler for Lambda
handler = Mangum(app, lifespan="off")

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        # Log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle health check
        if event.get('resource') == '/health':
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
        response = handler(event, context)
        logger.info(f"Handler response: {json.dumps(response)}")
        return response

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