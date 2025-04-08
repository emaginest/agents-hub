"""
RAG Agent Implementation

This module implements a specialized agent for Retrieval-Augmented Generation (RAG)
using the PGVector and Scraper tools from the agents-hub framework.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urlparse

from agents_hub import Agent
from agents_hub.llm.base import BaseLLM
from agents_hub.tools.standard import PGVectorTool, ScraperTool
from agents_hub.utils.document import chunk_text

# Configure logging
logger = logging.getLogger(__name__)


class RAGAgent:
    """
    Specialized agent for Retrieval-Augmented Generation (RAG).
    
    This class provides a high-level interface for:
    - Scraping and storing content from URLs
    - Querying the knowledge base
    - Managing collections
    
    Example:
        ```python
        from agents_hub import RAGAgent
        from agents_hub.llm.providers import OpenAIProvider
        
        # Initialize LLM provider
        llm = OpenAIProvider(api_key="your-openai-api-key")
        
        # Initialize RAG agent
        rag_agent = RAGAgent(
            llm=llm,
            pg_host="localhost",
            pg_port=5432,
            pg_database="postgres",
            pg_user="postgres",
            pg_password="postgres",
        )
        
        # Create a collection
        await rag_agent.create_collection("my_collection")
        
        # Scrape and store content from a URL
        await rag_agent.scrape_and_store(
            url="https://example.com",
            collection_name="my_collection",
        )
        
        # Answer a question
        result = await rag_agent.answer_question(
            question="What is the main topic of the website?",
            collection_name="my_collection",
        )
        print(result["answer"])
        ```
    """
    
    def __init__(
        self,
        llm: BaseLLM,
        pg_host: str = "localhost",
        pg_port: int = 5432,
        pg_database: str = "postgres",
        pg_user: str = "postgres",
        pg_password: str = "postgres",
        pg_schema: str = "public",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        chunk_method: str = "sentence",
        search_limit: int = 5,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the RAG agent.
        
        Args:
            llm: LLM provider for generating embeddings and responses
            pg_host: PostgreSQL host
            pg_port: PostgreSQL port
            pg_database: PostgreSQL database name
            pg_user: PostgreSQL username
            pg_password: PostgreSQL password
            pg_schema: PostgreSQL schema
            chunk_size: Size of chunks when processing documents
            chunk_overlap: Overlap between chunks
            chunk_method: Method for chunking documents (token, character, sentence)
            search_limit: Maximum number of results to return when searching
            system_prompt: Custom system prompt for the agent (optional)
        """
        self.llm = llm
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunk_method = chunk_method
        self.search_limit = search_limit
        
        # Initialize PGVector tool
        self.pgvector_tool = PGVectorTool(
            llm=llm,
            host=pg_host,
            port=pg_port,
            database=pg_database,
            user=pg_user,
            password=pg_password,
            schema=pg_schema,
        )
        
        # Initialize Scraper tool
        self.scraper_tool = ScraperTool()
        
        # Default system prompt
        default_system_prompt = """You are a knowledge management assistant specialized in Retrieval-Augmented Generation (RAG).
        
        Your capabilities include:
        1. Scraping and storing content from URLs
        2. Querying the knowledge base to retrieve relevant information
        3. Answering questions based on the retrieved information
        
        When answering questions:
        - First search for relevant information using the pgvector tool
        - Use the retrieved information to formulate your response
        - Cite the sources of information when possible
        - If you don't have relevant information, acknowledge it
        
        Always provide accurate, helpful, and concise responses based on the available information.
        """
        
        # Initialize agent
        self.agent = Agent(
            name="rag_agent",
            llm=llm,
            tools=[self.pgvector_tool, self.scraper_tool],
            system_prompt=system_prompt or default_system_prompt,
        )
    
    async def create_collection(self, collection_name: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new collection in the vector database.
        
        Args:
            collection_name: Name of the collection
            metadata: Optional metadata for the collection
            
        Returns:
            Result of the operation
        """
        logger.info(f"Creating collection: {collection_name}")
        
        result = await self.pgvector_tool.run({
            "operation": "create_collection",
            "collection_name": collection_name,
            "metadata": metadata or {},
        })
        
        return result
    
    async def list_collections(self) -> Dict[str, Any]:
        """
        List all collections in the vector database.
        
        Returns:
            List of collections
        """
        logger.info("Listing collections")
        
        result = await self.pgvector_tool.run({
            "operation": "list_collections",
        })
        
        return result
    
    async def delete_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        Delete a collection from the vector database.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Result of the operation
        """
        logger.info(f"Deleting collection: {collection_name}")
        
        result = await self.pgvector_tool.run({
            "operation": "delete_collection",
            "collection_name": collection_name,
        })
        
        return result
    
    async def count_documents(self, collection_name: str) -> Dict[str, Any]:
        """
        Count documents in a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Document count
        """
        logger.info(f"Counting documents in collection: {collection_name}")
        
        result = await self.pgvector_tool.run({
            "operation": "count_documents",
            "collection_name": collection_name,
        })
        
        return result
    
    async def scrape_url(self, url: str, extract_type: str = "text") -> Dict[str, Any]:
        """
        Scrape content from a URL.
        
        Args:
            url: URL to scrape
            extract_type: Type of content to extract (text, html, metadata, all)
            
        Returns:
            Scraped content
        """
        logger.info(f"Scraping URL: {url}")
        
        # Validate URL
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {"error": "Invalid URL format"}
        except Exception as e:
            logger.error(f"Invalid URL: {str(e)}")
            return {"error": f"Invalid URL: {str(e)}"}
        
        # Scrape the URL
        try:
            result = await self.scraper_tool.run({
                "url": url,
                "extract_type": extract_type,
            })
            
            return result
        except Exception as e:
            logger.error(f"Error scraping URL: {str(e)}")
            return {"error": f"Error scraping URL: {str(e)}"}
    
    async def store_document(
        self,
        document: str,
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store a document in the vector database.
        
        Args:
            document: Document text
            collection_name: Name of the collection
            metadata: Optional metadata for the document
            
        Returns:
            Result of the operation
        """
        logger.info(f"Storing document in collection: {collection_name}")
        
        # Store the document
        try:
            result = await self.pgvector_tool.run({
                "operation": "add_document",
                "document": document,
                "collection_name": collection_name,
                "metadata": metadata or {},
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "chunk_method": self.chunk_method,
            })
            
            return result
        except Exception as e:
            logger.error(f"Error storing document: {str(e)}")
            return {"error": f"Error storing document: {str(e)}"}
    
    async def scrape_and_store(
        self,
        url: str,
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Scrape content from a URL and store it in the vector database.
        
        Args:
            url: URL to scrape
            collection_name: Name of the collection
            metadata: Optional metadata for the document
            
        Returns:
            Result of the operation
        """
        logger.info(f"Scraping and storing content from URL: {url}")
        
        # Scrape the URL
        scrape_result = await self.scrape_url(url, extract_type="all")
        
        if "error" in scrape_result:
            return scrape_result
        
        # Extract text content
        text = scrape_result.get("text", "")
        
        if not text:
            logger.warning(f"No text content found in URL: {url}")
            return {"error": "No text content found in the URL"}
        
        # Prepare metadata
        doc_metadata = {
            "source": url,
            "title": scrape_result.get("metadata", {}).get("title", ""),
            "description": scrape_result.get("metadata", {}).get("description", ""),
            **metadata or {},
        }
        
        # Store the document
        store_result = await self.store_document(text, collection_name, doc_metadata)
        
        return {
            "scrape_result": scrape_result,
            "store_result": store_result,
            "url": url,
            "collection_name": collection_name,
        }
    
    async def search(
        self,
        query: str,
        collection_name: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search for documents in the vector database.
        
        Args:
            query: Search query
            collection_name: Name of the collection
            limit: Maximum number of results to return
            
        Returns:
            Search results
        """
        logger.info(f"Searching collection: {collection_name}")
        
        # Search the collection
        try:
            result = await self.pgvector_tool.run({
                "operation": "search",
                "query": query,
                "collection_name": collection_name,
                "limit": limit or self.search_limit,
            })
            
            return result
        except Exception as e:
            logger.error(f"Error searching collection: {str(e)}")
            return {"error": f"Error searching collection: {str(e)}"}
    
    async def answer_question(
        self,
        question: str,
        collection_name: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Answer a question using the RAG approach.
        
        Args:
            question: Question to answer
            collection_name: Name of the collection to search
            limit: Maximum number of results to return
            
        Returns:
            Answer and search results
        """
        logger.info(f"Answering question: {question}")
        
        # Search for relevant documents
        search_result = await self.search(question, collection_name, limit)
        
        if "error" in search_result:
            return search_result
        
        # Extract search results
        results = search_result.get("results", [])
        
        if not results:
            logger.warning(f"No relevant documents found for question: {question}")
            return {
                "answer": "I don't have enough information to answer this question.",
                "search_results": [],
                "question": question,
                "collection_name": collection_name,
            }
        
        # Prepare context from search results
        context = "\n\n".join([
            f"Document {i+1}:\n{result['document']}"
            for i, result in enumerate(results)
        ])
        
        # Generate answer using the agent
        prompt = f"""
        Question: {question}
        
        Please answer the question based on the following information:
        
        {context}
        
        Answer:
        """
        
        try:
            response = await self.agent.run(prompt)
            
            return {
                "answer": response,
                "search_results": results,
                "question": question,
                "collection_name": collection_name,
            }
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return {"error": f"Error generating answer: {str(e)}"}
    
    async def chat(self, message: str) -> str:
        """
        Chat with the agent directly.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        logger.info(f"Chat message: {message}")
        
        try:
            response = await self.agent.run(message)
            return response
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return f"Error: {str(e)}"
