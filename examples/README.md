# Testing Your Deployed RAG API

## Prerequisites

1. Get your API key from:
   - AWS Console > API Gateway > API Keys
   - CloudFormation stack outputs after deployment

2. Set up environment variables:
   ```bash
   # Create .env file
   cp ../.env.example .env

   # Edit .env and add your API key
   API_KEY=your-api-key-here
   ```

## Quick Start

1. Edit `test_api.py` and replace `{aws-host}` with your actual API Gateway endpoint host.

2. Install the required libraries:
```bash
pip install requests python-dotenv
```

3. Run the test script:
```bash
# Test with default question
python test_api.py

# Test with your own question
python test_api.py "What is machine learning?"
```

## Example Usage

1. Test the health endpoint:
```bash
python test_api.py
```

Expected output:
```
Testing health endpoint...

Health Check Response:
{
  "status": "healthy",
  "message": "RAG system is operational"
}

Testing predict endpoint with question: What is RAG?
...
```

2. Ask a specific question:
```bash
python test_api.py "Tell me about artificial intelligence"
```

Expected output:
```
Testing health endpoint...

Health Check Response:
{
  "status": "healthy",
  "message": "RAG system is operational"
}

Testing predict endpoint with question: Tell me about artificial intelligence

Question Response:
{
  "response": "Based on the provided context..."
}
```

## API Endpoints

### POST /rag/api/v1/predict
Ask a question to the RAG system.

Required headers:
- Content-Type: application/json
- X-API-Key: your-api-key-here

Request body:
```json
{
    "text": "Your question here"
}
```

### GET /health
Health check endpoint.

Required headers:
- X-API-Key: your-api-key-here

## Troubleshooting

1. If you get a 403 Forbidden error:
   - Verify your API key is correct in .env file
   - Check if the API key is active in AWS Console
   - Ensure you're using the correct header name (X-API-Key)

2. If you get a connection error:
   - Verify the API endpoint is correct
   - Check if the API is accessible from your network
   - Ensure the Lambda function and API Gateway are properly deployed

3. If you get a timeout:
   - The request might be taking too long
   - Check if your database is accessible from Lambda
   - Consider increasing the Lambda timeout

4. If you get an error response:
   - Check the error message in the response
   - Verify your request format
   - Check CloudWatch logs for detailed error information

## Alternative Methods

You can also use curl to test the API:

1. Health check:
```bash
curl https://{aws-host}/prod/health \
  -H "X-API-Key: your-api-key-here"
```

2. Ask a question:
```bash
curl -X POST https://{aws-host}/prod/rag/api/v1/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"text": "What is machine learning?"}'
```

For more examples and detailed API documentation, see `api_requests.md`.
