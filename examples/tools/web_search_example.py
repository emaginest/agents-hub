"""
Example of using the WebSearchTool in the Agents Hub framework.

This example demonstrates how to:
1. Initialize the WebSearchTool with a Tavily API key
2. Perform basic and advanced searches
3. Use the tool with an agent
4. Generate search context for RAG applications
5. Get direct answers to questions
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.tools.standard import WebSearchTool

# Load environment variables
load_dotenv()


async def main():
    """Run the example."""
    # Get API keys from environment variables
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    
    if not tavily_api_key:
        print("Error: TAVILY_API_KEY environment variable is required.")
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
    
    # Initialize the WebSearchTool
    web_search = WebSearchTool(api_key=tavily_api_key)
    
    # Example 1: Basic search
    print("\n=== Example 1: Basic Search ===")
    search_result = await web_search.run({"query": "Latest developments in quantum computing"})
    print(f"Search Results: {search_result}")
    
    # Example 2: Advanced search with parameters
    print("\n=== Example 2: Advanced Search with Parameters ===")
    advanced_search_result = await web_search.run({
        "query": "Climate change solutions",
        "search_depth": "advanced",
        "max_results": 3,
        "exclude_domains": ["wikipedia.org"],
        "include_answer": True,
    })
    print(f"Advanced Search Results: {advanced_search_result}")
    
    # Example 3: Using the tool with an agent
    print("\n=== Example 3: Using the Tool with an Agent ===")
    agent = Agent(
        name="web_researcher",
        llm=llm,
        tools=[web_search],
        system_prompt="You are a web researcher that can search the web for information. "
                     "Always use the web_search tool to find information before answering questions."
    )
    
    query = "What are the latest advancements in artificial intelligence? Provide a brief summary."
    print(f"Query: {query}")
    response = await agent.run(query)
    print(f"Agent Response: {response}")
    
    # Example 4: Generate search context for RAG
    print("\n=== Example 4: Generate Search Context for RAG ===")
    context = web_search.get_search_context("Space exploration recent missions")
    print(f"Search Context for RAG: {context}")
    
    # Example 5: Get direct answers to questions
    print("\n=== Example 5: Get Direct Answers to Questions ===")
    answer = web_search.qna_search("Who won the Nobel Prize in Physics in 2023?")
    print(f"Direct Answer: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
