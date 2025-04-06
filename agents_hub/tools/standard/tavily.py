"""
Tavily Search API tool for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import os
import asyncio
from tavily import TavilyClient
from agents_hub.tools.base import BaseTool

# Initialize logger
logger = logging.getLogger(__name__)


class TavilyTool(BaseTool):
    """
    Tool for searching the web using the Tavily Search API.

    This tool provides access to Tavily's search and extract capabilities,
    allowing agents to search the web and extract information from web pages.
    """

    # Define schema as a class variable
    schema = {
        "name": "tavily",
        "description": "Search the web for information using Tavily Search API.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["search", "extract"],
                    "description": "Operation to perform (search or extract)",
                },
                "query": {
                    "type": "string",
                    "description": "Search query (required for search operation)",
                },
                "url": {
                    "type": "string",
                    "description": "URL to extract information from (required for extract operation)",
                },
                "search_depth": {
                    "type": "string",
                    "enum": ["basic", "advanced"],
                    "description": "Depth of search (basic or advanced)",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                },
                "include_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of domains to include in search",
                },
                "exclude_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of domains to exclude from search",
                },
                "include_answer": {
                    "type": "boolean",
                    "description": "Whether to include an answer in search results",
                },
                "include_raw_content": {
                    "type": "boolean",
                    "description": "Whether to include raw content in search results",
                },
                "extract_type": {
                    "type": "string",
                    "enum": ["text", "structured"],
                    "description": "Type of extraction to perform (text or structured)",
                },
            },
            "required": [],
        },
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        search_depth: str = "basic",
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
    ):
        """
        Initialize the Tavily tool.

        Args:
            api_key: Tavily API key (defaults to environment variable)
            search_depth: Depth of search ("basic" or "advanced")
            max_results: Maximum number of results to return
            include_domains: List of domains to include in search
            exclude_domains: List of domains to exclude from search
        """
        # Initialize the base tool with name, description, and parameters
        super().__init__(
            name=self.schema["name"],
            description=self.schema["description"],
            parameters=self.schema["parameters"],
        )

        # Use provided API key or get from environment
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not self.api_key:
            logger.warning("No Tavily API key provided. Set TAVILY_API_KEY environment variable or pass api_key parameter.")

        self.client = TavilyClient(api_key=self.api_key)
        self.search_depth = search_depth
        self.max_results = max_results
        self.include_domains = include_domains or []
        self.exclude_domains = exclude_domains or []

    async def run(self, args: Union[Dict[str, Any], str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the Tavily tool.

        Args:
            args: Tool arguments (dict or string)
            context: Context information

        Returns:
            Tool results
        """
        try:
            # Check if API key is available
            if not self.api_key:
                return {"error": "Tavily API key is required. Set TAVILY_API_KEY environment variable or pass api_key parameter."}

            # Handle string arguments (convert to dict)
            if isinstance(args, str):
                # If args is a string, assume it's a search query
                args = {"operation": "search", "query": args}

            # Get operation type
            operation = args.get("operation", "search")

            if operation == "search":
                return await self._search(args, context)
            elif operation == "extract":
                return await self._extract(args, context)
            else:
                return {"error": f"Unknown operation: {operation}. Supported operations are 'search' and 'extract'."}

        except Exception as e:
            logger.exception(f"Error in Tavily tool: {e}")
            return {"error": f"Error in Tavily tool: {str(e)}"}

    async def _search(self, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search the web using Tavily Search API.

        Args:
            args: Search arguments
            context: Context information

        Returns:
            Search results
        """
        # Get search parameters
        query = args.get("query")
        if not query:
            return {"error": "Query is required for search operation"}

        search_depth = args.get("search_depth", self.search_depth)
        max_results = args.get("max_results", self.max_results)
        include_domains = args.get("include_domains", self.include_domains)
        exclude_domains = args.get("exclude_domains", self.exclude_domains)
        include_answer = args.get("include_answer", True)
        include_raw_content = args.get("include_raw_content", False)

        # Perform search
        try:
            # Use the synchronous method with asyncio.to_thread
            response = await asyncio.to_thread(
                self.client.search,
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
            )

            # Format results
            results = {
                "query": query,
                "results": response.get("results", []),
            }

            if include_answer and "answer" in response:
                results["answer"] = response["answer"]

            return results

        except Exception as e:
            logger.exception(f"Error in Tavily search: {e}")
            return {"error": f"Error in Tavily search: {str(e)}"}

    async def _extract(self, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract information from a URL using Tavily Extract API.

        Args:
            args: Extract arguments
            context: Context information

        Returns:
            Extraction results
        """
        # Get extract parameters
        url = args.get("url")
        if not url:
            return {"error": "URL is required for extract operation"}

        extract_type = args.get("extract_type", "text")

        # Perform extraction
        try:
            # Use the synchronous method with asyncio.to_thread
            response = await asyncio.to_thread(
                self.client.extract,
                url=url,
                extract_type=extract_type,
            )

            # Format results
            results = {
                "url": url,
                "content": response.get("content", ""),
                "title": response.get("title", ""),
            }

            return results

        except Exception as e:
            logger.exception(f"Error in Tavily extract: {e}")
            return {"error": f"Error in Tavily extract: {str(e)}"}

    # Removed _run_async method as we're using asyncio.to_thread directly

    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the Tavily tool.

        Returns:
            Tool schema
        """
        return self.schema
