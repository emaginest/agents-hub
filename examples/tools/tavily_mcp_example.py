"""
Example of using Tavily MCP server with the Agents Hub framework.
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.tools.standard import TavilyTool


async def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()

    # Check if Tavily API key is available
    if not os.environ.get("TAVILY_API_KEY"):
        print("Tavily API key is missing. Please set the TAVILY_API_KEY environment variable.")
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

    # Create Tavily tool
    tavily_tool = TavilyTool(
        api_key=os.environ.get("TAVILY_API_KEY"),
        search_depth="basic",
        max_results=3,
    )

    # Create an agent with the Tavily tool
    agent = Agent(
        name="tavily_agent",
        llm=llm,
        tools=[tavily_tool],
        system_prompt="You are an assistant that can search the web using Tavily. Use the tavily tool to search for information and extract content from web pages.",
    )

    # Example 1: Search for information
    print("\n=== Example 1: Search for Information ===")
    query = "What are the latest developments in renewable energy?"
    response = await agent.run(f"Search for information about: {query}")
    print(f"Response: {response}")

    # Example 2: Extract information from a URL
    print("\n=== Example 2: Extract Information from a URL ===")
    url = "https://www.energy.gov/eere/renewable-energy"
    response = await agent.run(f"Extract and summarize the content from this URL: {url}")
    print(f"Response: {response}")

    # Note: Examples 3 and 4 have been removed due to issues with tool calls


if __name__ == "__main__":
    asyncio.run(main())
