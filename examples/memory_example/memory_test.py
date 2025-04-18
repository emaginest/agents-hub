"""
Example demonstrating long-term memory with PostgreSQL in agents-hub.

This example shows how to:
1. Create an agent with PostgreSQL memory
2. Have conversations that persist across sessions
3. Retrieve past conversations

Usage:
    # Start PostgreSQL with Docker
    docker-compose up -d postgres

    # Run the example
    python memory_test.py
"""

import os
import asyncio
import uuid
from datetime import datetime
import argparse
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider, ClaudeProvider, OllamaProvider
from agents_hub.memory.backends import PostgreSQLMemory

# Load environment variables from .env file
load_dotenv()


async def test_memory(llm_provider="openai", conversation_id=None, clear_memory=False):
    """
    Test memory functionality with the specified LLM provider.

    Args:
        llm_provider: LLM provider to use (openai, anthropic, ollama)
        conversation_id: Optional conversation ID to continue
        clear_memory: Whether to clear memory for the conversation
    """
    # Initialize LLM provider
    if llm_provider == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable not set.")
            print("Please set it in a .env file or export it in your shell.")
            return

        llm = OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"],
            model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
        )
    elif llm_provider == "anthropic":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("Error: ANTHROPIC_API_KEY environment variable not set.")
            print("Please set it in a .env file or export it in your shell.")
            return

        llm = ClaudeProvider(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            model=os.environ.get("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
        )
    elif llm_provider == "ollama":
        llm = OllamaProvider(
            model=os.environ.get("OLLAMA_MODEL", "llama3"),
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    else:
        print(f"Error: Unknown LLM provider '{llm_provider}'")
        return

    # Initialize PostgreSQL memory
    memory = PostgreSQLMemory(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ.get("POSTGRES_DB", "agents_hub"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        table_prefix="agents_hub_",
    )

    # Create agent with memory
    agent = Agent(
        name="memory_agent",
        llm=llm,
        memory=memory,
        system_prompt="You are an assistant that remembers past conversations. When the user refers to something mentioned in a previous conversation, recall it and respond appropriately.",
    )

    # Generate a conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        print(f"Starting new conversation with ID: {conversation_id}")
    else:
        print(f"Continuing conversation with ID: {conversation_id}")

    # Clear memory if requested
    if clear_memory:
        print(f"Clearing memory for conversation ID: {conversation_id}")
        await memory.clear_history(conversation_id)

    # Get conversation history
    history = await memory.get_history(conversation_id)
    if history:
        print(f"Found {len(history)} previous interactions in this conversation.")
        print("Last interaction:")
        last = history[-1]
        print(f"User: {last['user_message']}")
        print(f"Assistant: {last['assistant_message']}")
        print(f"Timestamp: {last['timestamp']}")
        print()
    else:
        print("No previous interactions found for this conversation.")
        print()

    # Interactive chat loop
    print("Type 'exit' to end the conversation.")
    print("Type 'stats' to see memory statistics.")
    print("Type 'history' to see conversation history.")
    print("Type 'search <query>' to search memory.")
    print()

    while True:
        user_input = input("User: ")

        if user_input.lower() == "exit":
            break

        if user_input.lower() == "stats":
            stats = await memory.get_statistics(conversation_id)
            print("Memory Statistics:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
            print()
            continue

        if user_input.lower() == "history":
            history = await memory.get_history(conversation_id)
            print(f"Conversation History (ID: {conversation_id}):")
            for i, interaction in enumerate(history):
                print(f"Interaction {i+1} ({interaction['timestamp']}):")
                print(f"  User: {interaction['user_message']}")
                print(f"  Assistant: {interaction['assistant_message']}")
                print()
            continue

        if user_input.lower().startswith("search "):
            query = user_input[7:].strip()
            results = await memory.search_memory(query, conversation_id)
            print(f"Search Results for '{query}':")
            for i, result in enumerate(results):
                print(f"Result {i+1} ({result['timestamp']}):")
                print(f"  User: {result['user_message']}")
                print(f"  Assistant: {result['assistant_message']}")
                print()
            continue

        # Get response from agent
        response = await agent.run(
            user_input, context={"conversation_id": conversation_id}
        )
        print(f"Assistant: {response}")
        print()


async def main():
    parser = argparse.ArgumentParser(
        description="Test memory functionality in agents-hub"
    )
    parser.add_argument(
        "--llm",
        choices=["openai", "anthropic", "ollama"],
        default="openai",
        help="LLM provider to use",
    )
    parser.add_argument(
        "--conversation", type=str, default=None, help="Conversation ID to continue"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear memory for the conversation"
    )

    args = parser.parse_args()

    await test_memory(
        llm_provider=args.llm,
        conversation_id=args.conversation,
        clear_memory=args.clear,
    )


if __name__ == "__main__":
    asyncio.run(main())
