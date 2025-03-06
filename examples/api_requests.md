# Making Requests to the Deployed RAG API

## Authentication

All requests require an API key to be sent in the `X-API-Key` header:
```
X-API-Key: your-api-key-here
```

You can get your API key from:
1. AWS Console > API Gateway > API Keys
2. CloudFormation stack outputs after deployment

## Using curl

1. Ask a question:
```bash
curl -X POST https://{aws-host}/prod/rag/api/v1/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"text": "your question here"}'
```

2. Health check:
```bash
curl https://{aws-host}/prod/health \
  -H "X-API-Key: your-api-key-here"
```

## Using Python with requests

```python
import requests

# API configuration
BASE_URL = "https://{aws-host}/prod"
API_KEY = "your-api-key-here"

# Common headers
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

def ask_question(question: str) -> dict:
    """Send a question to the RAG API"""
    response = requests.post(
        f"{BASE_URL}/rag/api/v1/predict",
        json={"text": question},
        headers=headers
    )
    return response.json()

def check_health() -> dict:
    """Check API health"""
    response = requests.get(
        f"{BASE_URL}/health",
        headers=headers
    )
    return response.json()

# Example usage
if __name__ == "__main__":
    # Ask a question
    question = "What is the capital of France?"
    result = ask_question(question)
    print(f"Question: {question}")
    print(f"Answer: {result['response']}")

    # Check health
    health = check_health()
    print(f"API Health: {health}")
```

## Using Python with aiohttp (Async)

```python
import asyncio
import aiohttp

# API configuration
BASE_URL = "https://{aws-host}/prod"
API_KEY = "your-api-key-here"

# Common headers
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

async def ask_question_async(question: str) -> dict:
    """Send a question to the RAG API asynchronously"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/rag/api/v1/predict",
            json={"text": question},
            headers=headers
        ) as response:
            return await response.json()

async def check_health_async() -> dict:
    """Check API health asynchronously"""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{BASE_URL}/health",
            headers=headers
        ) as response:
            return await response.json()

# Example usage
async def main():
    # Ask a question
    question = "What is the capital of France?"
    result = await ask_question_async(question)
    print(f"Question: {question}")
    print(f"Answer: {result['response']}")

    # Check health
    health = await check_health_async()
    print(f"API Health: {health}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Example Response Formats

### POST /rag/api/v1/predict
Request:
```json
{
    "text": "What is the capital of France?"
}
```

Response:
```json
{
    "response": "Based on the provided context, I cannot answer questions about the capital of France. The context does not contain information about French geography or cities."
}
```

### GET /health
Response:
```json
{
    "status": "healthy",
    "message": "RAG system is operational"
}
```

## Notes

1. Replace `{aws-host}` with your actual API Gateway endpoint host.
2. Replace `your-api-key-here` with your actual API key.
3. The API expects and returns JSON data.
4. For production use, consider adding:
   - Error handling
   - Retry logic
   - Request timeouts
   - API key rotation

## Troubleshooting

1. If you get a 403 Forbidden error:
   - Verify your API key is correct
   - Check if the API key is active in AWS Console
   - Ensure you're using the correct header name (X-API-Key)

2. If you get a 504 Gateway Timeout:
   - The Lambda function might be taking too long to respond
   - Consider increasing the Lambda timeout in the CloudFormation template

3. If you get a 429 Too Many Requests:
   - You might be hitting the API Gateway rate limits
   - Check the usage plan limits in AWS Console
   - Consider requesting a rate limit increase

4. If you get a CORS error in a web browser:
   - Add the appropriate headers to your request
   - Contact the API administrator to allow your domain
