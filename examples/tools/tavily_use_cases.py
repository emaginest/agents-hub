"""
Example of Tavily use cases in the Agents Hub framework.
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.tools.standard import TavilyTool


async def simple_search_example(agent):
    """Run a simple search example."""
    print("\n=== Simple Search Example ===")

    # Example: Simple search
    query = "What are the latest developments in AI?"
    prompt = f"Please search for information about: {query}"

    response = await agent.run(prompt)
    print(f"Response: {response}")


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
        search_depth="advanced",
        max_results=7,
    )

    # Create an agent with the Tavily tool
    agent = Agent(
        name="research_agent",
        llm=llm,
        tools=[tavily_tool],
        system_prompt="""
        You are a professional research assistant with expertise in gathering and analyzing information.
        You can search the web for up-to-date information and extract content from web pages.
        When providing information:
        - Always cite your sources with URLs
        - Organize information in a clear, structured format
        - Prioritize reliable and authoritative sources
        - Provide balanced perspectives when appropriate
        - Indicate when information might be incomplete or uncertain
        """,
    )

    # Run the example
    await simple_search_example(agent)


if __name__ == "__main__":
    asyncio.run(main())
