"""
Example of creating a simple MCP server that can be used with the MCPTool.

This example demonstrates how to:
1. Create a simple MCP server using the FastMCP class
2. Define tools, resources, and prompts
3. Run the server with stdio or SSE transport

Usage:
    # Install required packages
    pip install "mcp[cli]"

    # Run the server with stdio transport
    python mcp_server_example.py

    # Run the server with SSE transport
    python mcp_server_example.py --transport sse --port 8050
"""

import argparse
import json
import os
from mcp.server.fastmcp import FastMCP, Image

# Create an MCP server
mcp = FastMCP("Example Server")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
def get_weather(city: str) -> str:
    """Get the weather for a city (simulated)."""
    weather_data = {
        "New York": {"temperature": 72, "condition": "Sunny"},
        "London": {"temperature": 65, "condition": "Cloudy"},
        "Tokyo": {"temperature": 80, "condition": "Rainy"},
        "Sydney": {"temperature": 85, "condition": "Clear"},
    }

    if city in weather_data:
        data = weather_data[city]
        return f"The weather in {city} is {data['condition']} with a temperature of {data['temperature']}°F."
    else:
        return f"Weather data for {city} is not available."


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    return f"Hello, {name}! Welcome to the MCP server example."


@mcp.resource("info://server")
def get_server_info() -> str:
    """Get information about the server."""
    return """
    # MCP Server Example

    This is a simple MCP server example that demonstrates how to create a server
    that can be used with the MCPTool in the Agents Hub framework.

    ## Available Tools

    - `add`: Add two numbers
    - `multiply`: Multiply two numbers
    - `get_weather`: Get the weather for a city (simulated)

    ## Available Resources

    - `greeting://{name}`: Get a personalized greeting
    - `info://server`: Get information about the server
    """


@mcp.prompt()
def math_problem(a: int, b: int) -> str:
    """Create a math problem prompt."""
    return f"""
    Please solve the following math problem:

    If I have {a} apples and I get {b} more, how many apples do I have in total?
    """


@mcp.prompt()
def weather_query(city: str) -> str:
    """Create a weather query prompt."""
    return f"""
    Please tell me about the weather in {city}.
    What's the temperature and conditions?
    """


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run an MCP server example")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport mechanism to use (stdio or sse)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Port to use for SSE transport",
    )
    args = parser.parse_args()

    # Run the server
    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        # Set the port before running
        mcp.port = args.port
        mcp.run(transport="sse")
