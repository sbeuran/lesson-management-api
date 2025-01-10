from mangum import Mangum
from .routes import app
import json
import logging
from decimal import Decimal

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create Mangum handler for Lambda
handler = Mangum(app)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(DecimalEncoder, self).default(obj)

def format_response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "body": json.dumps(body, cls=DecimalEncoder),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type,X-Api-Key"
        }
    }

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        # Handle CORS preflight requests
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,X-Api-Key"
                }
            }

        # Process the request through Mangum
        response = handler(event, context)
        logger.info(f"Handler response: {json.dumps(response)}")

        # If response is already formatted, return it
        if isinstance(response, dict) and "statusCode" in response:
            return response

        # Format the response
        if isinstance(response, dict):
            return format_response(200, response)
        elif isinstance(response, list):
            return format_response(200, {"items": response})
        else:
            return format_response(200, {"result": response})

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return format_response(500, {"error": str(e)}) 