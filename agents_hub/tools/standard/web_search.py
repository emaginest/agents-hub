"""
Web search tool for the Agents Hub framework using Tavily API.

This module provides a tool for searching the web using the Tavily API,
which offers powerful search capabilities with relevant and up-to-date results.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import os
import json
from agents_hub.tools.base import BaseTool

try:
    from tavily import TavilyClient
except ImportError:
    raise ImportError(
        "The tavily-python package is required to use the WebSearchTool. "
        "Please install it with `pip install tavily-python`."
    )

# Initialize logger
logger = logging.getLogger(__name__)


class WebSearchTool(BaseTool):
    """
    Tool for searching the web using Tavily API.
    
    This tool provides methods for searching the web and retrieving relevant information.
    
    Example:
        ```python
        from agents_hub.tools.standard import WebSearchTool
        
        # Initialize Web Search tool with API key
        web_search = WebSearchTool(api_key="your-tavily-api-key")
        
        # Use the tool
        result = await web_search.run({
            "query": "Latest developments in quantum computing",
        })
        ```
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the web search tool.
        
        Args:
            api_key: Tavily API key. If not provided, will look for TAVILY_API_KEY environment variable.
        """
        super().__init__(
            name="web_search",
            description="Search the web for information",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "search_depth": {
                        "type": "string",
                        "enum": ["basic", "advanced"],
                        "description": "The depth of the search. 'advanced' is more thorough but may take longer.",
                        "default": "basic",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-20)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20,
                    },
                    "include_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of domains to specifically include in the search results",
                    },
                    "exclude_domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of domains to specifically exclude from the search results",
                    },
                    "include_answer": {
                        "type": "boolean",
                        "description": "Whether to include an AI-generated answer based on search results",
                        "default": False,
                    },
                    "include_raw_content": {
                        "type": "boolean",
                        "description": "Whether to include the raw content of each search result",
                        "default": False,
                    },
                },
                "required": ["query"],
            },
        )
        
        # Get API key from parameters or environment variable
        self.api_key = api_key or os.environ.get("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Tavily API key is required. Either pass it as a parameter or set the TAVILY_API_KEY environment variable."
            )
        
        # Initialize Tavily client
        self.client = TavilyClient(api_key=self.api_key)
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Search the web using Tavily API.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Search results
        """
        # Extract parameters
        query = parameters.get("query")
        if not query:
            return {"error": "Query parameter is required"}
        
        search_depth = parameters.get("search_depth", "basic")
        max_results = parameters.get("max_results", 5)
        include_domains = parameters.get("include_domains", [])
        exclude_domains = parameters.get("exclude_domains", [])
        include_answer = parameters.get("include_answer", False)
        include_raw_content = parameters.get("include_raw_content", False)
        
        # Validate parameters
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            return {"error": "max_results must be an integer between 1 and 20"}
        
        try:
            # Perform the search
            logger.info(f"Searching for: {query}")
            
            # Convert include_answer to the format expected by Tavily
            include_answer_param = include_answer
            if isinstance(include_answer, bool) and include_answer:
                include_answer_param = "basic"
            
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                include_answer=include_answer_param,
                include_raw_content=include_raw_content,
            )
            
            # Return the search results
            return response
            
        except Exception as e:
            logger.error(f"Error searching with Tavily: {str(e)}")
            return {"error": f"Search failed: {str(e)}"}
    
    def get_search_context(self, query: str, max_results: int = 5) -> str:
        """
        Get a formatted context string from search results for use in RAG applications.
        
        Args:
            query: The search query
            max_results: Maximum number of results to include in the context
            
        Returns:
            Formatted context string
        """
        try:
            # Perform the search
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
            )
            
            # Format the results as a context string
            context = f"Search results for: {query}\n\n"
            
            for i, result in enumerate(response.get("results", [])):
                context += f"[{i+1}] {result.get('title')}\n"
                context += f"URL: {result.get('url')}\n"
                context += f"{result.get('content')}\n\n"
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting search context: {str(e)}")
            return f"Error retrieving search context: {str(e)}"
    
    def qna_search(self, query: str) -> str:
        """
        Get a direct answer to a question using Tavily's search and answer generation.
        
        Args:
            query: The question to answer
            
        Returns:
            Generated answer
        """
        try:
            # Perform the search with answer generation
            response = self.client.search(
                query=query,
                search_depth="advanced",
                include_answer="advanced",
                max_results=5,
            )
            
            # Return the generated answer
            return response.get("answer", "No answer was generated for this query.")
            
        except Exception as e:
            logger.error(f"Error in QnA search: {str(e)}")
            return f"Error retrieving answer: {str(e)}"
