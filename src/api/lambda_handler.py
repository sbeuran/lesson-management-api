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
            "Access-Control-Allow-Origin": "*"
        }
    }

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle CORS preflight
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,X-Api-Key"
                }
            }

        # Add API Gateway context
        if 'requestContext' not in event:
            event['requestContext'] = {}
        if 'path' not in event:
            event['path'] = event.get('resource', '')
            
        # Add path parameters if they exist
        if 'pathParameters' in event and event['pathParameters']:
            event['path'] = event['path'].format(**event['pathParameters'])

        # Process request
        response = handler(event, context)
        logger.info(f"Raw handler response: {json.dumps(response)}")

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
                    "Access-Control-Allow-Origin": "*"
                }
            }
        else:
            return format_response(200, {"data": str(response)})

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(500, {"error": str(e)}) 