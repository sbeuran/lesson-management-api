from mangum import Mangum
from .routes import app
import json
import logging
from decimal import Decimal
import traceback

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create Mangum handler for Lambda
handler = Mangum(app, lifespan="off")  # Turn off lifespan to avoid FastAPI startup issues

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super(DecimalEncoder, self).default(obj)

def format_response(status_code: int, body: dict):
    try:
        return {
            "statusCode": status_code,
            "body": json.dumps(body, cls=DecimalEncoder),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,X-Api-Key",
                "Access-Control-Allow-Credentials": "true"
            }
        }
    except Exception as e:
        logger.error(f"Error formatting response: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error during response formatting"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
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
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,X-Api-Key",
                    "Access-Control-Allow-Credentials": "true"
                }
            }

        # Process the request through Mangum
        try:
            response = handler(event, context)
            logger.info(f"Raw handler response: {json.dumps(response)}")
        except Exception as e:
            logger.error(f"Handler error: {str(e)}")
            logger.error(traceback.format_exc())
            return format_response(500, {"error": f"Handler error: {str(e)}"})

        # If response is already formatted, return it
        if isinstance(response, dict) and "statusCode" in response:
            logger.info(f"Returning pre-formatted response: {json.dumps(response)}")
            return response

        # Format the response
        if isinstance(response, dict):
            logger.info("Formatting dict response")
            return format_response(200, response)
        elif isinstance(response, list):
            logger.info("Formatting list response")
            return format_response(200, {"items": response})
        else:
            logger.info(f"Formatting other response type: {type(response)}")
            return format_response(200, {"result": response})

    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_response(500, {"error": str(e)}) 