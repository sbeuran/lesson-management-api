from mangum import Mangum
from .routes import app
import json
import logging
from decimal import Decimal
import traceback
from datetime import datetime
from fastapi.responses import JSONResponse

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

def format_response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "body": json.dumps(body, cls=DecimalEncoder),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,X-Api-Key,Authorization"
        }
    }

def lambda_handler(event, context):
    try:
        # Log the incoming event
        logger.info(f"Received event: {json.dumps(event)}")

        # Direct health check response
        if event.get('rawPath', '') == '/health' or event.get('path', '') == '/health':
            return format_response(200, {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            })

        # Handle CORS preflight
        if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
            return format_response(200, {"message": "OK"})

        # Process request through Mangum
        try:
            response = handler(event, context)
            logger.info(f"Handler response: {json.dumps(response)}")
            return response
        except Exception as e:
            logger.error(f"Handler error: {str(e)}")
            logger.error(traceback.format_exc())
            return format_response(500, {
                "error": str(e),
                "type": type(e).__name__
            })

    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(500, {
            "error": str(e),
            "type": type(e).__name__
        }) 