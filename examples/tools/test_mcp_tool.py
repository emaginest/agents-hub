"""
Test script for the MCPTool implementation.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import the agents_hub package
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from agents_hub.tools.standard import MCPTool


async def test_sse_transport():
    """Test the MCPTool with SSE transport."""
    print("\n=== Testing MCPTool with SSE Transport ===\n")

    # Create an MCP tool using SSE transport and use it as a context manager
    async with MCPTool(
        server_name="example-server",
        server_url="http://localhost:8000/sse",
        transport="sse",
    ) as sse_tool:
        # List available tools
        print("Listing available tools...")
        tools_result = await sse_tool.run({"operation": "list_tools"})
        print("Available tools:")
        for tool in tools_result.get("tools", []):
            print(f"  - {tool['name']}: {tool['description']}")

        # Call the add tool
        print("\nCalling 'add' tool...")
        add_result = await sse_tool.run(
            {
                "operation": "call_tool",
                "tool_name": "add",
                "tool_arguments": {"a": 10, "b": 20},
            }
        )
        print(f"Result: {add_result}")

        # Call the get_weather tool
        print("\nCalling 'get_weather' tool...")
        weather_result = await sse_tool.run(
            {
                "operation": "call_tool",
                "tool_name": "get_weather",
                "tool_arguments": {"city": "London"},
            }
        )
        print(f"Result: {weather_result}")

        # List available resources
        print("\nListing available resources...")
        resources_result = await sse_tool.run({"operation": "list_resources"})
        print("Available resources:")
        for resource in resources_result.get("resources", []):
            print(f"  - {resource['name']}: {resource['description']}")

        # Read a resource
        print("\nReading 'greeting://MCPTool' resource...")
        resource_result = await sse_tool.run(
            {
                "operation": "read_resource",
                "resource_path": "greeting://MCPTool",
            }
        )
        print(f"Result: {resource_result}")

        # List available prompts
        print("\nListing available prompts...")
        prompts_result = await sse_tool.run({"operation": "list_prompts"})
        print("Available prompts:")
        for prompt in prompts_result.get("prompts", []):
            print(f"  - {prompt['name']}: {prompt['description']}")

        # Get a prompt
        print("\nGetting 'weather_query' prompt...")
        prompt_result = await sse_tool.run(
            {
                "operation": "get_prompt",
                "prompt_name": "weather_query",
                "prompt_arguments": {"city": "Tokyo"},
            }
        )
        print(f"Result: {prompt_result}")

        print("\nAll operations completed successfully!")


async def test_manual_cleanup():
    """Test the MCPTool with manual cleanup."""
    print("\n=== Testing MCPTool with Manual Cleanup ===\n")

    # Create an MCP tool
    sse_tool = MCPTool(
        server_name="example-server-manual",
        server_url="http://localhost:8000/sse",
        transport="sse",
    )

    try:
        # List available tools
        print("Listing available tools...")
        tools_result = await sse_tool.run({"operation": "list_tools"})
        print("Available tools:")
        for tool in tools_result.get("tools", []):
            print(f"  - {tool['name']}: {tool['description']}")

        # Call a tool
        print("\nCalling 'add' tool...")
        add_result = await sse_tool.run(
            {
                "operation": "call_tool",
                "tool_name": "add",
                "tool_arguments": {"a": 5, "b": 7},
            }
        )
        print(f"Result: {add_result}")

        print("\nOperations completed successfully!")
    finally:
        # Manually close the tool
        print("\nManually closing the tool...")
        await sse_tool.close()
        print("Tool closed successfully!")


async def main():
    """Run all tests."""
    # Test with context manager (recommended)
    await test_sse_transport()

    # Test with manual cleanup
    await test_manual_cleanup()


if __name__ == "__main__":
    asyncio.run(main())
