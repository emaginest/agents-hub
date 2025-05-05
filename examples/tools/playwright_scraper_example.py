"""
Example of using the PlaywrightScraperTool for advanced web scraping.

This example demonstrates how to:
1. Scrape JavaScript-heavy websites
2. Handle dynamic content
3. Implement anti-detection techniques
4. Extract specific content using selectors
5. Execute JavaScript scenarios
"""

import asyncio
import os
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import PlaywrightScraperTool

# Load environment variables
load_dotenv()

# Initialize LLM provider
llm = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the Playwright scraper tool
playwright_scraper = PlaywrightScraperTool()


# Helper function to safely print result content
def safe_print_result(result, key, max_chars=500):
    """Safely print result content with error handling."""
    if "error" in result:
        print(f"Error: {result['error']}")
        return False

    if key in result:
        content = (
            result[key][:max_chars] if len(result[key]) > max_chars else result[key]
        )
        print(f"{key.capitalize()}: {content}...")
        return True
    else:
        print(f"No {key} found in result: {result.keys()}")
        return False


async def example_basic_scraping():
    """Example of basic scraping with Playwright."""
    print("\n=== Basic Scraping Example ===")

    # Create an agent with the Playwright scraper tool
    agent = Agent(
        name="web_researcher",
        llm=llm,
        tools=[playwright_scraper],
        system_prompt="You are a web researcher that can scrape and analyze web content from JavaScript-heavy websites.",
    )

    # Use the agent to scrape a more reliable website instead of Reddit
    print("Asking agent to scrape and summarize MDN Web Docs Python page...")
    response = await agent.run(
        "Scrape and summarize the content from https://developer.mozilla.org/en-US/docs/Learn/Python"
    )
    print(f"Agent response: {response}")


async def example_direct_tool_usage():
    """Example of using the Playwright scraper tool directly."""
    print("\n=== Direct Tool Usage Example ===")

    # Basic scraping
    result = await playwright_scraper.run(
        {
            "url": "https://news.ycombinator.com/",
            "extract_type": "text",
            "timeout": 60000,  # Increase timeout to 60 seconds
        }
    )

    print("Scraped text from Hacker News:")
    if safe_print_result(result, "text"):
        # Scraping with a specific selector
        result = await playwright_scraper.run(
            {
                "url": "https://news.ycombinator.com/",
                "extract_type": "text",
                "selector": ".titleline > a",
                "timeout": 60000,  # Increase timeout to 60 seconds
            }
        )

        print("\nScraped titles from Hacker News:")
        safe_print_result(result, "text")

    # Try a different site instead of Amazon (which often blocks scrapers)
    print("\nScraping MDN Web Docs for Python:")
    result = await playwright_scraper.run(
        {
            "url": "https://developer.mozilla.org/en-US/docs/Learn/Python",
            "extract_type": "text",
            "selector": "h1, h2, h3",  # Get headings
            "stealth_mode": True,
            "timeout": 60000,  # Increase timeout to 60 seconds
        }
    )

    safe_print_result(result, "text")


async def example_js_scenario():
    """Example of using JavaScript scenarios for interaction."""
    print("\n=== JavaScript Scenario Example ===")

    try:
        # Scrape GitHub trending repositories
        result = await playwright_scraper.run(
            {
                "url": "https://github.com/trending",
                "extract_type": "text",
                "selector": "article.Box-row h1",
                "wait_for_selector": "article.Box-row",
                "timeout": 60000,  # Increase timeout to 60 seconds
                "js_scenario": [
                    # Select the "Python" language from the dropdown
                    {"click": {"selector": "[data-hovercard-type='language']"}},
                    {"wait_for_selector": {"selector": "a[href='/trending/python']"}},
                    {"click": {"selector": "a[href='/trending/python']"}},
                    {"wait_for_navigation": {"timeout": 5000}},
                ],
            }
        )

        print("Trending Python repositories:")
        safe_print_result(result, "text")
    except Exception as e:
        print(f"Error in JavaScript scenario example: {str(e)}")
        print("This could be due to changes in GitHub's UI structure.")
        print(
            "Try running the example with a different website or updating the selectors."
        )


async def example_infinite_scroll():
    """Example of handling infinite scroll pages."""
    print("\n=== Infinite Scroll Example ===")

    try:
        # Use a more reliable site for infinite scroll example
        result = await playwright_scraper.run(
            {
                "url": "https://news.ycombinator.com/",
                "extract_type": "text",
                "selector": ".athing",
                "wait_for_selector": ".athing",
                "scroll_to_bottom": True,
                "timeout": 60000,  # Increase timeout to 60 seconds
            }
        )

        print("Scraped items with scroll:")
        safe_print_result(result, "text")
    except Exception as e:
        print(f"Error in infinite scroll example: {str(e)}")


async def main():
    """Run all examples."""
    try:
        await example_basic_scraping()
        await example_direct_tool_usage()
        await example_js_scenario()
        await example_infinite_scroll()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print(
            "Make sure you have installed Playwright browsers with: playwright install"
        )


if __name__ == "__main__":
    asyncio.run(main())
