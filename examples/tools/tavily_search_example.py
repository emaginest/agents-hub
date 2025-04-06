"""
Example of using the Tavily Search API tool in the Agents Hub framework.
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
        max_results=5,
    )
    
    # Create an agent with the Tavily tool
    agent = Agent(
        name="research_agent",
        llm=llm,
        tools=[tavily_tool],
        system_prompt="You are a research assistant that can search the web for information. Use the tavily tool to search for information when needed. Always cite your sources.",
    )
    
    # Example 1: Basic search
    print("\n=== Example 1: Basic Search ===")
    query = "What are the latest developments in quantum computing?"
    response = await agent.run(f"Search for information about: {query}")
    print(f"Response: {response}")
    
    # Example 2: Search with specific domains
    print("\n=== Example 2: Search with Specific Domains ===")
    query = "What are the environmental impacts of electric vehicles?"
    response = await agent.run(
        f"Search for information about {query}, but only from educational (.edu) and government (.gov) websites."
    )
    print(f"Response: {response}")
    
    # Example 3: Search with advanced depth
    print("\n=== Example 3: Search with Advanced Depth ===")
    query = "What are the ethical considerations of artificial intelligence?"
    response = await agent.run(
        f"I need a comprehensive analysis of {query}. Please use advanced search depth to get more detailed information."
    )
    print(f"Response: {response}")
    
    # Example 4: Search with answer synthesis
    print("\n=== Example 4: Search with Answer Synthesis ===")
    query = "How does climate change affect biodiversity?"
    response = await agent.run(
        f"I need a concise answer about {query}. Please synthesize the information from multiple sources."
    )
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
