"""
Example of integrating the MCP (Model Context Protocol) tool with agents in the Agents Hub framework.

This example demonstrates how to:
1. Create an agent with an MCP tool connected to a custom MCP server
2. Use the agent to perform mathematical operations and get weather information
3. Properly manage MCP tool resources with try/finally

Before running this example, start the MCP server with:
    python examples/tools/mcp_server_example.py --transport sse

Usage:
    # Install required packages
    pip install "mcp[cli]"

    # Run the example
    python mcp_agent_example.py
"""

import os
import asyncio
import logging
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.tools.standard import MCPTool

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def agent_with_mcp_tool():
    """Example of an agent using an MCP tool with SSE transport."""
    print("\n=== Agent with MCP Tool (SSE Transport) ===\n")

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

    # Create an MCP tool using SSE transport
    # The tool name will be "mcp_example-server" (prefix "mcp_" is added automatically)
    mcp_tool = MCPTool(
        server_name="example-server",
        server_url="http://localhost:8000/sse",
        transport="sse",
    )

    try:
        # Create an agent with the MCP tool
        agent = Agent(
            name="mcp_agent",
            llm=llm,
            tools=[mcp_tool],
            system_prompt=(
                "You are an assistant that can use a custom MCP server to perform various operations. "
                "You have access to a tool called mcp_example-server that can perform mathematical operations "
                "and provide weather information.\n\n"
                "IMPORTANT: Always use the exact tool name 'mcp_example-server' when calling the tool.\n\n"
                "To add two numbers, use:\n"
                "```\n"
                "{\n"
                '  "operation": "call_tool",\n'
                '  "tool_name": "add",\n'
                '  "tool_arguments": {"a": 5, "b": 3}\n'
                "}\n"
                "```\n\n"
                "To multiply two numbers, use:\n"
                "```\n"
                "{\n"
                '  "operation": "call_tool",\n'
                '  "tool_name": "multiply",\n'
                '  "tool_arguments": {"a": 4, "b": 7}\n'
                "}\n"
                "```\n\n"
                "To get weather information for a city, use:\n"
                "```\n"
                "{\n"
                '  "operation": "call_tool",\n'
                '  "tool_name": "get_weather",\n'
                '  "tool_arguments": {"city": "New York"}\n'
                "}\n"
                "```\n\n"
                "When asked to perform calculations or get weather information, use the appropriate tool."
            ),
        )

        # First, let's list the available tools
        print("Listing available tools...")
        tools_response = await mcp_tool.run({"operation": "list_tools"})
        print(f"\nAvailable tools: {tools_response}")

        # Use the agent to add two numbers
        query = "What is 25 + 17? Use the mcp_example-server tool to calculate this."
        print(f"\nAsking agent to add two numbers...\nQuery: {query}")
        response = await agent.run(query)
        print(f"\nAgent response:\n{response}")

        # Use the agent to multiply two numbers
        query = "What is 8 × 12? Use the mcp_example-server tool to calculate this."
        print(f"\nAsking agent to multiply two numbers...\nQuery: {query}")
        response = await agent.run(query)
        print(f"\nAgent response:\n{response}")

        # Use the agent to get weather information
        query = "What's the weather like in Tokyo? Use the mcp_example-server tool to find out."
        print(f"\nAsking agent to get weather information...\nQuery: {query}")
        response = await agent.run(query)
        print(f"\nAgent response:\n{response}")

        # Let the agent decide which tool to use
        query = (
            "I need to calculate the area of a rectangle that is 15 meters long and 8 meters wide. "
            "Also, tell me what the weather is like in London. Use the appropriate tools."
        )
        print(f"\nLetting the agent decide which tool to use...\nQuery: {query}")
        response = await agent.run(query)
        print(f"\nAgent response:\n{response}")
    finally:
        # Always close the tool to clean up resources
        print("\nCleaning up resources...")
        await mcp_tool.close()
        print("Resources cleaned up successfully!")


async def main():
    """Run the example."""
    print("Starting the example...")

    try:
        # Run the agent example
        print("Running agent example...")
        await agent_with_mcp_tool()
    except Exception as e:
        print(f"Error running agent example: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("Example completed")


if __name__ == "__main__":
    asyncio.run(main())
