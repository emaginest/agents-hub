"""
Example of using Langfuse monitoring in the Agents Hub framework.

This example demonstrates:
- Basic conversation tracking
- Tool usage tracking
- Token usage and cost tracking
- User ID tracking
- Conversation scoring and user feedback
"""

import os
import asyncio
import datetime
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
    if not all(
        [
            os.environ.get("LANGFUSE_PUBLIC_KEY"),
            os.environ.get("LANGFUSE_SECRET_KEY"),
        ]
    ):
        print(
            "Langfuse credentials are missing. Please set the following environment variables:"
        )
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
        host=os.environ.get("LANGFUSE_HOST", "https://langfuse.thejourney.health"),
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

    # Example 1: Basic conversation with user ID
    print("\n=== Example 1: Basic Conversation with User ID ===")
    conversation_id = "example1_run2_" + datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    user_id = "test_user_2025_04_20_1"
    query = "What is the capital of France?"
    response = await agent.run(
        query, context={"conversation_id": conversation_id, "user_id": user_id}
    )
    print(f"Response: {response}")

    # Add a score for the conversation
    await monitor.score_conversation(
        conversation_id=conversation_id,
        name="relevance",
        value=0.95,
        comment="Provided a direct and accurate answer",
        user_id=user_id,
    )

    # Add user feedback
    await monitor.add_user_feedback(
        conversation_id=conversation_id,
        score=5,  # 5-star rating
        comment="Perfect answer, exactly what I needed!",
        user_id=user_id,
    )

    # Example 2: Using a tool with token tracking
    print("\n=== Example 2: Using a Tool with Token Tracking ===")
    conversation_id = "example2_run2_" + datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    user_id = "test_user_2025_04_20_2"
    query = "What is the square root of 144?"

    # We'll manually count tokens for this example
    input_tokens = len(query.split()) * 1.3  # Rough approximation

    response = await agent.run(
        query,
        context={
            "conversation_id": conversation_id,
            "user_id": user_id,
            "input_tokens": int(input_tokens),  # Pass token count to the monitor
        },
    )
    print(f"Response: {response}")

    # The output tokens and cost will be automatically calculated by the monitor

    # Example 3: Multiple turns in a conversation with user ID and token tracking
    print("\n=== Example 3: Multiple Turns with User ID and Token Tracking ===")
    conversation_id = "example3_run2_" + datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    user_id = "test_user_2025_04_20_3"

    # First turn
    query1 = "Hello, I need help with some math problems."
    response1 = await agent.run(
        query1, context={"conversation_id": conversation_id, "user_id": user_id}
    )
    print(f"Response 1: {response1}")

    # Second turn
    query2 = "What is 25 squared?"
    response2 = await agent.run(
        query2, context={"conversation_id": conversation_id, "user_id": user_id}
    )
    print(f"Response 2: {response2}")

    # Third turn
    query3 = "Now divide that by 5."
    response3 = await agent.run(
        query3, context={"conversation_id": conversation_id, "user_id": user_id}
    )
    print(f"Response 3: {response3}")

    # Add a score for the entire conversation
    await monitor.score_conversation(
        conversation_id=conversation_id,
        name="helpfulness",
        value=0.9,
        comment="Maintained context across multiple turns",
        user_id=user_id,
    )

    # Example 4: Error handling with user ID
    print("\n=== Example 4: Error Handling with User ID ===")
    conversation_id = "example4_run2_" + datetime.datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )
    user_id = "test_user_2025_04_20_4"
    try:
        # Intentionally cause an error by passing invalid parameters
        query = "Calculate 1/0"
        response = await agent.run(
            query, context={"conversation_id": conversation_id, "user_id": user_id}
        )
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error caught: {e}")
        # Manually track the error
        await monitor.track_error(
            error=str(e),
            conversation_id=conversation_id,
            user_id=user_id,
            metadata={"query": query},
        )

    # Example 5: View token usage and cost summary
    print("\n=== Example 5: Token Usage and Cost Summary ===")
    print("Token usage and cost information is automatically tracked")
    print("Check the Langfuse dashboard to see detailed analytics including:")
    print("- Total tokens used across all conversations")
    print("- Cost breakdown by model and conversation")
    print("- User engagement metrics")
    print("- Performance analytics")

    print("\nCheck the Langfuse dashboard to see the monitored conversations!")
    print("URL: https://langfuse.thejourney.health")


if __name__ == "__main__":
    asyncio.run(main())
