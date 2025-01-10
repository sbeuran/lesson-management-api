from mangum import Mangum
from .routes import app
import json

# Create Mangum handler for Lambda
handler = Mangum(app)

# Add error handling
def format_error_response(status_code: int, message: str):
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": message}),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    }

# Wrap the handler to add error handling and CORS
def lambda_handler(event, context):
    try:
        # Handle CORS preflight requests
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type"
                }
            }

        # Process the request through Mangum
        response = handler(event, context)
        
        # Add CORS headers to the response
        if isinstance(response, dict) and "headers" in response:
            response["headers"].update({
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            })
        
        return response

    except Exception as e:
        return format_error_response(500, str(e)) 