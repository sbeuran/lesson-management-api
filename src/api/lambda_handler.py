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
            "Access-Control-Allow-Headers": "Content-Type,X-Api-Key"
        }
    }

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle CORS preflight
        if event.get("httpMethod") == "OPTIONS":
            return format_response(200, {"message": "OK"})

        # Add path parameters to event if they exist
        if event.get('pathParameters'):
            path = event.get('path', '')
            for key, value in event['pathParameters'].items():
                path = path.replace(f"{{{key}}}", value)
            event['path'] = path

        # Process request through Mangum
        try:
            response = handler(event, context)
            logger.info(f"Handler response: {json.dumps(response)}")
        except Exception as e:
            logger.error(f"Handler error: {str(e)}")
            logger.error(traceback.format_exc())
            return format_response(500, {"error": str(e)})

        # Format response
        if isinstance(response, dict):
            if "statusCode" not in response:
                return format_response(200, response)
            return response
        elif isinstance(response, list):
            return format_response(200, {"items": response})
        else:
            return format_response(200, {"data": str(response)})

    except Exception as e:
        logger.error(f"Lambda error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(500, {"error": str(e)}) 