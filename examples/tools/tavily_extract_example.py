"""
Example of using the Tavily Extract API tool in the Agents Hub framework.
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
    )

    # Create an agent with the Tavily tool
    agent = Agent(
        name="extract_agent",
        llm=llm,
        tools=[tavily_tool],
        system_prompt="You are a web content analyzer that can extract and analyze information from web pages. Use the tavily tool with the extract operation to get content from URLs.",
    )

    # Example 1: Extract text from a webpage
    print("\n=== Example 1: Extract Text from a Webpage ===")
    url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    response = await agent.run(f"Extract and summarize the content from this URL: {url}")
    print(f"Response: {response}")

    # Example 2: Extract and analyze specific information
    print("\n=== Example 2: Extract and Analyze Specific Information ===")
    url = "https://www.nasa.gov/solar-system/nasa-confirms-water-on-sunlit-surface-of-moon/"
    response = await agent.run(
        f"Extract information from this URL: {url} and explain the significance of the discovery."
    )
    print(f"Response: {response}")

    # Example 3: Compare information from multiple sources
    print("\n=== Example 3: Compare Information from Multiple Sources ===")
    url1 = "https://climate.nasa.gov/evidence/"
    url2 = "https://www.un.org/en/climatechange/science/causes-effects-climate-change"

    # Extract from the first URL
    response1 = await agent.run(f"Extract information from this URL: {url1}")
    print(f"Information from first URL: {response1}\n")

    # Extract from the second URL
    response2 = await agent.run(f"Extract information from this URL: {url2}")
    print(f"Information from second URL: {response2}\n")

    # Compare the information
    response = await agent.run(
        f"I have information from two sources about climate change evidence.\n\n"
        f"Source 1 (NASA): {response1}\n\n"
        f"Source 2 (UN): {response2}\n\n"
        f"Compare and contrast how these two sources present evidence for climate change."
    )
    print(f"Response: {response}")

    # Example 4: Extract structured information
    print("\n=== Example 4: Extract Structured Information ===")
    url = "https://www.who.int/news-room/fact-sheets/detail/climate-change-and-health"
    response = await agent.run(
        f"Extract information from this URL: {url} and create a structured list of "
        f"health impacts of climate change mentioned in the article."
    )
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
