"""
Example of using the MCP tool in the Agents Hub framework.
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.tools.standard import MCPTool


async def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()
    
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
    
    # Create an MCP tool for filesystem access
    filesystem_tool = MCPTool(
        server_name="filesystem",
        server_command="npx",
        server_args=["-y", "@modelcontextprotocol/server-filesystem", "./"],
        transport="stdio",
    )
    
    # Create an agent with the MCP tool
    agent = Agent(
        name="mcp_agent",
        llm=llm,
        tools=[filesystem_tool],
        system_prompt="You are an assistant that can access the filesystem. Use the mcp_filesystem tool to list and read files.",
        description="Assistant that can access the filesystem using MCP",
    )
    
    # Example 1: List resources (files and directories)
    print("\n=== Example 1: List Resources ===")
    query = "List all the resources available through the filesystem MCP server."
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 2: Read a file
    print("\n=== Example 2: Read a File ===")
    query = "Read the content of the README.md file and summarize it."
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 3: List files in a directory
    print("\n=== Example 3: List Files in a Directory ===")
    query = "List all the Python files in the agents_hub directory."
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 4: Find specific information
    print("\n=== Example 4: Find Specific Information ===")
    query = "Find all files that contain information about the MCP tool and tell me what they do."
    response = await agent.run(query)
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
