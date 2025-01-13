# Lesson Completion API

A serverless API built with FastAPI and AWS Lambda for tracking student lesson completions.

## Overview

This API provides endpoints to record and retrieve lesson completion data for students. It uses AWS services including Lambda, API Gateway, and DynamoDB for a scalable, serverless architecture.

## Project Structure
```
lesson-completion-api/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── lambda_handler.py  # Mangum handler for AWS Lambda
│   │   └── routes.py         # FastAPI endpoints and business logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── lesson.py        # Pydantic model for lesson completion
│   └── services/
│       ├── __init__.py
│       └── dynamodb.py      # DynamoDB interaction layer
├── tests/
│   └── test_lesson_api.py   # API integration tests with mocked DynamoDB
├── .github/
│   └── workflows/
│       └── main.yml         # GitHub Actions for CI/CD
├── lesson-completion-api.postman_collection.json  # API test collection
└── requirements.txt         # Project dependencies
```

## API Documentation

### Health Check
```http
GET /health
```

Response:
```json
{
    "status": "healthy",
    "message": "API and database are operational"
}
```

### Complete Lesson
```http
POST /lessons/complete
```

Request:
```json
{
    "student_id": "student123",
    "lesson_id": "lesson456",
    "completed_at": "2024-01-13T00:11:00Z"
}
```

Response:
```json
{
    "message": "Lesson completion recorded",
    "completion_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Get Student Completions
```http
GET /lessons/completions/{student_id}
```

Response:
```json
{
    "student_id": "student123",
    "completions": [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "student_id": "student123",
            "lesson_id": "lesson456",
            "completed_at": "2024-01-13T00:11:00Z",
            "created_at": "2024-01-13T00:11:01Z"
        }
    ]
}
```

## AWS Infrastructure

### DynamoDB
- Table Name: `lesson_completions`
- Primary Key: 
  - Partition Key: `student_id` (String)
  - Sort Key: `id` (String)
- Attributes:
  - `lesson_id` (String)
  - `completed_at` (String)
  - `created_at` (String)

### Lambda Function
- Runtime: Python 3.9
- Handler: `src.api.lambda_handler.handler`
- Memory: 256MB
- Timeout: 30 seconds

### API Gateway
- Type: REST API
- Authentication: API Key required
- Stage: prod
- Endpoints:
  - GET /health
  - POST /lessons/complete
  - GET /lessons/completions/{student_id}

## Local Development

### Prerequisites
- Python 3.9+
- AWS CLI configured
- Postman

### Setup
1. Clone repository:
```bash
git clone <repository-url>
cd lesson-completion-api
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export TESTING=true
```

## Testing

### Unit Tests
Run tests with coverage:
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing -v
```

### Postman Tests
1. Import collection:
   - File: `lesson-completion-api.postman_collection.json`
2. Set environment variables:
   - `baseUrl`: Your API Gateway URL
   - `apiKey`: Your API key

## Deployment

### Automated (GitHub Actions)
Push to main branch triggers:
1. Run tests
2. Create/update AWS resources
3. Deploy Lambda function
4. Configure API Gateway
5. Update API documentation

### Manual Deployment
Package and deploy:
```bash
# Create deployment package
pip install -r requirements.txt -t package/
cd package && zip -r ../deployment.zip . && cd ..
zip -g deployment.zip src/*

# Update Lambda
aws lambda update-function-code \
    --function-name lesson-completion-api \
    --zip-file fileb://deployment.zip
```

## Security

### API Security
- API Key required in `x-api-key` header
- IAM roles for Lambda and DynamoDB
- Secrets managed via GitHub Actions secrets

### Monitoring
- CloudWatch Logs for Lambda
- API Gateway metrics
- DynamoDB performance metrics

## Contributing
1. Create feature branch
2. Add tests
3. Create pull request
4. Ensure CI passes

## License
MIT License
