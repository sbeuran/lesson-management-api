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

        # Add API Gateway context
        if 'requestContext' not in event:
            event['requestContext'] = {}
        if 'path' not in event:
            event['path'] = event.get('resource', '')

        # Fix path parameters
        if 'pathParameters' in event and event['pathParameters']:
            event['path'] = event.get('resource', '').replace('{student_id}', event['pathParameters']['student_id'])

        # Process request
        try:
            response = handler(event, context)
            logger.info(f"Raw handler response: {json.dumps(response)}")
        except Exception as e:
            logger.error(f"Handler error: {str(e)}")
            logger.error(traceback.format_exc())
            return format_response(500, {"error": f"Handler error: {str(e)}"})

        # Handle FastAPI Response objects
        if isinstance(response, dict):
            if "statusCode" not in response:
                return format_response(200, response)
            return response
        elif isinstance(response, JSONResponse):
            return {
                "statusCode": response.status_code,
                "body": response.body.decode(),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,X-Api-Key"
                }
            }
        else:
            return format_response(200, {"data": str(response)})

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(500, {"error": str(e)}) 