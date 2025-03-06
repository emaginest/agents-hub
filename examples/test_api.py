import requests
import json
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Replace this with your actual API Gateway endpoint and API key
API_ENDPOINT = "https://{aws-host}/prod"
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("Error: API_KEY environment variable is not set")
    sys.exit(1)


def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get(
            f"{API_ENDPOINT}/health", headers={"X-API-Key": API_KEY}
        )
        print("\nHealth Check Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error checking health: {str(e)}")


def ask_question(question):
    """Send a question to the RAG API"""
    try:
        response = requests.post(
            f"{API_ENDPOINT}/rag/api/v1/predict",
            json={"text": question},
            headers={"Content-Type": "application/json", "X-API-Key": API_KEY},
        )
        print("\nQuestion Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error asking question: {str(e)}")


if __name__ == "__main__":
    # Test health endpoint
    print("Testing health endpoint...")
    test_health()

    # Test predict endpoint
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is RAG?"
    print(f"\nTesting predict endpoint with question: {question}")
    ask_question(question)
