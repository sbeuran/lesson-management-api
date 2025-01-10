from mangum import Mangum
from .routes import app
import json
import logging

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create Mangum handler for Lambda
handler = Mangum(app)

def format_error_response(status_code: int, message: str):
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": message}),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
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
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type,X-Api-Key"
                }
            }

        # Process the request through Mangum
        response = handler(event, context)
        logger.info(f"Handler response: {json.dumps(response)}")
        
        # Add CORS headers to the response
        if isinstance(response, dict):
            if "headers" not in response:
                response["headers"] = {}
            
            response["headers"].update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,X-Api-Key"
            })
        
        return response

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return format_error_response(500, str(e)) 