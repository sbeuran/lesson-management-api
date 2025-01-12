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

def lambda_handler(event, context):
    try:
        # Log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle health check
        if event.get('path') == '/health':
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat()
                })
            }

        # Process request through Mangum
        return handler(event, context)

    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        } 