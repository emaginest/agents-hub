"""
Example of using Langfuse monitoring in the Agents Hub framework.
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.tools.standard import CalculatorTool
from agents_hub.monitoring import LangfuseMonitor


async def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if Langfuse credentials are available
    if not all([
        os.environ.get("LANGFUSE_PUBLIC_KEY"),
        os.environ.get("LANGFUSE_SECRET_KEY"),
    ]):
        print("Langfuse credentials are missing. Please set the following environment variables:")
        print("  LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY")
        return
    
    # Create LLM provider
    if os.environ.get("OPENAI_API_KEY"):
        print("Using OpenAI provider")
        llm = OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"],
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        )
    else:
        print("Using Ollama provider (local)")
        llm = OllamaProvider(
            model=os.environ.get("OLLAMA_MODEL", "llama3"),
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    
    # Create a calculator tool
    calculator_tool = CalculatorTool()
    
    # Create a Langfuse monitor
    monitor = LangfuseMonitor(
        public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
        secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        host=os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com"),
        release="1.0.0",  # Optional version tracking
        debug=True,  # Enable debug mode
    )
    
    # Create an agent with monitoring
    agent = Agent(
        name="monitored_agent",
        llm=llm,
        tools=[calculator_tool],
        system_prompt="You are a helpful assistant that can perform calculations. Use the calculator tool when needed.",
        description="Assistant with monitoring capabilities",
        monitor=monitor,
    )
    
    # Example 1: Basic conversation
    print("\n=== Example 1: Basic Conversation ===")
    conversation_id = "example1"
    query = "What is the capital of France?"
    response = await agent.run(query, context={"conversation_id": conversation_id})
    print(f"Response: {response}")
    
    # Example 2: Using a tool
    print("\n=== Example 2: Using a Tool ===")
    conversation_id = "example2"
    query = "What is the square root of 144?"
    response = await agent.run(query, context={"conversation_id": conversation_id})
    print(f"Response: {response}")
    
    # Example 3: Multiple turns in a conversation
    print("\n=== Example 3: Multiple Turns in a Conversation ===")
    conversation_id = "example3"
    
    # First turn
    query1 = "Hello, I need help with some math problems."
    response1 = await agent.run(query1, context={"conversation_id": conversation_id})
    print(f"Response 1: {response1}")
    
    # Second turn
    query2 = "What is 25 squared?"
    response2 = await agent.run(query2, context={"conversation_id": conversation_id})
    print(f"Response 2: {response2}")
    
    # Third turn
    query3 = "Now divide that by 5."
    response3 = await agent.run(query3, context={"conversation_id": conversation_id})
    print(f"Response 3: {response3}")
    
    # Example 4: Error handling
    print("\n=== Example 4: Error Handling ===")
    conversation_id = "example4"
    try:
        # Intentionally cause an error by passing invalid parameters
        query = "Calculate 1/0"
        response = await agent.run(query, context={"conversation_id": conversation_id})
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error caught: {e}")
    
    print("\nCheck the Langfuse dashboard to see the monitored conversations!")
    print("URL: https://cloud.langfuse.com")


if __name__ == "__main__":
    asyncio.run(main())
