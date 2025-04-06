"""
Web scraping tool for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import aiohttp
from bs4 import BeautifulSoup
import re
import json
from agents_hub.tools.base import BaseTool

# Initialize logger
logger = logging.getLogger(__name__)


class ScraperTool(BaseTool):
    """Tool for scraping web content."""
    
    def __init__(self):
        """Initialize the scraper tool."""
        super().__init__(
            name="web_scraper",
            description="Scrape content from a web page",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to scrape",
                    },
                    "extract_type": {
                        "type": "string",
                        "enum": ["text", "html", "metadata", "all"],
                        "description": "Type of content to extract",
                        "default": "text",
                    },
                    "selector": {
                        "type": "string",
                        "description": "Optional CSS selector to extract specific content",
                    },
                    "include_images": {
                        "type": "boolean",
                        "description": "Whether to include image URLs in the result",
                        "default": False,
                    },
                },
                "required": ["url"],
            },
        )
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Scrape content from a web page.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Scraped content
        """
        url = parameters.get("url")
        extract_type = parameters.get("extract_type", "text")
        selector = parameters.get("selector")
        include_images = parameters.get("include_images", False)
        
        try:
            # Fetch the page
            response_text = await self._fetch_url(url)
            
            # Return HTML if requested
            if extract_type == "html":
                return {"html": response_text, "url": url}
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response_text, "lxml")
            
            # Apply selector if provided
            if selector:
                elements = soup.select(selector)
                if not elements:
                    return {"error": f"No elements found matching selector: {selector}", "url": url}
                
                content = "\n".join(el.get_text(strip=True) for el in elements)
                
                # Extract images if requested
                images = []
                if include_images:
                    for el in elements:
                        images.extend(self._extract_images(el))
                
                return {
                    "text": content,
                    "images": images if include_images else None,
                    "url": url,
                }
            
            # Extract based on type
            if extract_type == "text":
                # Extract main content
                content = self._extract_main_content(soup)
                
                # Extract images if requested
                images = []
                if include_images:
                    images = self._extract_images(soup)
                
                return {
                    "text": content,
                    "images": images if include_images else None,
                    "url": url,
                }
            
            elif extract_type == "metadata":
                # Extract metadata
                metadata = self._extract_metadata(soup, url)
                return {"metadata": metadata, "url": url}
            
            elif extract_type == "all":
                # Extract everything
                content = self._extract_main_content(soup)
                metadata = self._extract_metadata(soup, url)
                
                # Extract images if requested
                images = []
                if include_images:
                    images = self._extract_images(soup)
                
                return {
                    "text": content,
                    "metadata": metadata,
                    "html": response_text,
                    "images": images if include_images else None,
                    "url": url,
                }
            
        except Exception as e:
            logger.exception(f"Error scraping URL: {e}")
            return {"error": str(e), "url": url}
    
    async def _fetch_url(self, url: str) -> str:
        """
        Fetch a URL with proper headers and error handling.
        
        Args:
            url: URL to fetch
            
        Returns:
            Response text
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=30) as response:
                response.raise_for_status()
                return await response.text()
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract the main content from a web page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Extracted text
        """
        # Create a copy of the soup to modify
        content_soup = BeautifulSoup(str(soup), "lxml")
        
        # Remove script, style, and navigation elements
        for element in content_soup(["script", "style", "header", "footer", "nav", "aside"]):
            element.extract()
        
        # Get text
        text = content_soup.get_text(separator="\n", strip=True)
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        """
        Extract metadata from a web page.
        
        Args:
            soup: BeautifulSoup object
            url: URL of the page
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "",
        }
        
        # Extract Open Graph metadata
        for meta in soup.find_all("meta"):
            if meta.get("property") and meta["property"].startswith("og:"):
                property_name = meta["property"][3:]
                metadata[property_name] = meta.get("content", "")
            
            # Extract description
            if meta.get("name") == "description":
                metadata["description"] = meta.get("content", "")
            
            # Extract keywords
            if meta.get("name") == "keywords":
                metadata["keywords"] = meta.get("content", "")
        
        # Extract JSON-LD structured data
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    if "@type" in data:
                        metadata["schema_type"] = data["@type"]
                    if "name" in data and not metadata.get("title"):
                        metadata["title"] = data["name"]
                    if "description" in data and not metadata.get("description"):
                        metadata["description"] = data["description"]
            except:
                pass
        
        return metadata
    
    def _extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract images from a web page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            List of image information
        """
        images = []
        
        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "")
            
            if src:
                # Skip tiny images, data URLs, and icons
                if (
                    re.search(r'(icon|logo|button|badge|pixel|tracking)', src.lower()) or
                    src.startswith("data:") or
                    re.search(r'\.svg$', src.lower())
                ):
                    continue
                
                images.append({
                    "url": src,
                    "alt": alt,
                })
        
        return images
