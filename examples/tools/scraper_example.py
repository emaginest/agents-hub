"""
Example of using the scraper tool in the Agents Hub framework.
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.tools.standard import ScraperTool


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
    
    # Create a scraper tool
    scraper_tool = ScraperTool()
    
    # Create an agent with the scraper tool
    agent = Agent(
        name="web_researcher",
        llm=llm,
        tools=[scraper_tool],
        system_prompt="You are a web researcher that can scrape and analyze web content. Use the web_scraper tool to fetch information from websites when needed.",
        description="Web researcher that can scrape and analyze web content",
    )
    
    # Example 1: Basic text extraction
    print("\n=== Example 1: Basic Text Extraction ===")
    query = "Scrape the content from https://en.wikipedia.org/wiki/Artificial_intelligence and summarize the key points about AI history."
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 2: Extracting specific content with a selector
    print("\n=== Example 2: Extracting Specific Content with a Selector ===")
    query = "Scrape the table of contents from https://en.wikipedia.org/wiki/Artificial_intelligence using the CSS selector '#toc'."
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 3: Extracting metadata
    print("\n=== Example 3: Extracting Metadata ===")
    query = "Get the metadata (title, description, etc.) from https://www.openai.com/"
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 4: Comparing information from multiple sources
    print("\n=== Example 4: Comparing Information from Multiple Sources ===")
    query = "Compare the definitions of machine learning from https://en.wikipedia.org/wiki/Machine_learning and https://www.ibm.com/topics/machine-learning"
    response = await agent.run(query)
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
