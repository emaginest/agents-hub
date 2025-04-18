"""
Test script to verify that the PGVector connection issue has been fixed.
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.vector_stores import PGVector

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def main():
    """Run the test script."""
    # Load environment variables from .env file
    load_dotenv()

    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")
        return

    # Print environment variables for debugging
    logger.info(f"POSTGRES_HOST: {os.environ.get('POSTGRES_HOST', 'Not set')}")
    logger.info(f"POSTGRES_PORT: {os.environ.get('POSTGRES_PORT', 'Not set')}")
    logger.info(f"POSTGRES_DB: {os.environ.get('POSTGRES_DB', 'Not set')}")
    logger.info(f"POSTGRES_USER: {os.environ.get('POSTGRES_USER', 'Not set')}")
    
    # Initialize LLM provider
    logger.info("Initializing OpenAI LLM provider...")
    llm = OpenAIProvider(
        api_key=api_key,
        model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
    )

    # Initialize PGVector tool with explicit connection parameters
    logger.info("Initializing PGVector tool...")
    pgvector_tool = PGVector(
        llm=llm,
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ.get("POSTGRES_DB", "agents_hub"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
    )

    # Create an agent with the PGVector tool
    logger.info("Creating agent with PGVector tool...")
    agent = Agent(
        name="test_agent",
        llm=llm,
        tools=[pgvector_tool],
        system_prompt="You are a test agent for verifying PGVector functionality."
    )

    # Test creating a collection
    logger.info("Testing collection creation...")
    collection_name = "test_collection"
    create_result = await agent.run(
        f"Create a new collection called '{collection_name}' for testing."
    )
    logger.info(f"Agent response: {create_result}")

    logger.info("Test completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
