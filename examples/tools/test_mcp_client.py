"""
Simple test client for the MCP server example.
"""

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client


async def main():
    """Test the MCP server."""
    print("Connecting to MCP server at http://localhost:8000/sse...")

    # Connect to the server using SSE
    async with sse_client("http://localhost:8000/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_result = await session.list_tools()
            print("\nAvailable tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Call the add tool
            print("\nCalling 'add' tool with arguments: a=2, b=3")
            result = await session.call_tool("add", arguments={"a": 2, "b": 3})
            print(f"Result: {result.content[0].text}")

            # Call the multiply tool
            print("\nCalling 'multiply' tool with arguments: a=4, b=5")
            result = await session.call_tool("multiply", arguments={"a": 4, "b": 5})
            print(f"Result: {result.content[0].text}")

            # Call the get_weather tool
            print("\nCalling 'get_weather' tool with argument: city='New York'")
            result = await session.call_tool(
                "get_weather", arguments={"city": "New York"}
            )
            print(f"Result: {result.content[0].text}")

            # List available resources
            resources_result = await session.list_resources()
            print("\nAvailable resources:")
            for resource in resources_result.resources:
                print(f"  - {resource.name}: {resource.description}")

            # Read a resource
            print("\nReading 'greeting://World' resource")
            content, mime_type = await session.read_resource("greeting://World")
            print(f"Content: {content}")
            print(f"MIME type: {mime_type}")

            # List available prompts
            prompts_result = await session.list_prompts()
            print("\nAvailable prompts:")
            for prompt in prompts_result.prompts:
                print(f"  - {prompt.name}: {prompt.description}")

            # Get a prompt
            print("\nGetting 'math_problem' prompt with arguments: a=10, b=5")
            prompt_result = await session.get_prompt(
                "math_problem", arguments={"a": "10", "b": "5"}
            )
            print(f"Prompt description: {prompt_result.description}")
            print(f"Prompt messages: {prompt_result.messages[0].content.text}")


if __name__ == "__main__":
    asyncio.run(main())
