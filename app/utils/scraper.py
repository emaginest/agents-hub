import aiohttp
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple
import logging


async def scrape_url(url: str) -> Tuple[str, Dict[str, str]]:
    """
    Scrape content from a URL and return the text content and metadata.

    Args:
        url: The URL to scrape

    Returns:
        Tuple containing:
        - Extracted text content
        - Metadata dictionary with url and title
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                html = await response.text()

        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text content
        text = soup.get_text(separator="\n", strip=True)

        # Get title
        title = soup.title.string if soup.title else url

        # Create metadata
        metadata = {"url": url, "title": title}

        return text, metadata

    except Exception as e:
        logging.error(f"Error scraping URL {url}: {str(e)}")
        raise Exception(f"Failed to scrape URL {url}: {str(e)}")


async def scrape_urls(urls: List[str]) -> List[Tuple[str, Dict[str, str]]]:
    """
    Scrape content from multiple URLs concurrently.

    Args:
        urls: List of URLs to scrape

    Returns:
        List of tuples, each containing:
        - Extracted text content
        - Metadata dictionary
    """
    results = []
    for url in urls:
        try:
            result = await scrape_url(url)
            results.append(result)
        except Exception as e:
            logging.error(f"Skipping URL {url} due to error: {str(e)}")
            continue
    return results
