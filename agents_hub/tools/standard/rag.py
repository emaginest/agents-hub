"""
RAG (Retrieval-Augmented Generation) tool for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union, BinaryIO
import logging
import base64
import json
import os
from agents_hub.tools.base import BaseTool
from agents_hub.tools.standard.scraper import ScraperTool
from agents_hub.knowledge.rag.backends.postgres import PostgreSQLVectorStorage
from agents_hub.utils.document import extract_text_from_pdf, extract_text_from_docx, chunk_text

# Initialize logger
logger = logging.getLogger(__name__)


class RAGTool(BaseTool):
    """Tool for Retrieval-Augmented Generation."""
    
    def __init__(self, vector_store: PostgreSQLVectorStorage):
        """
        Initialize the RAG tool.
        
        Args:
            vector_store: Vector storage backend
        """
        super().__init__(
            name="rag",
            description="Query or ingest documents for retrieval-augmented generation",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["query", "ingest", "list_collections", "delete_document", "delete_collection"],
                        "description": "Operation to perform",
                    },
                    "query": {
                        "type": "string",
                        "description": "Query for retrieving documents (for query operation)",
                    },
                    "collection_name": {
                        "type": "string",
                        "description": "Name of the collection to use",
                        "default": "default",
                    },
                    "document": {
                        "type": "string",
                        "description": "Document text to ingest (for ingest operation)",
                    },
                    "document_id": {
                        "type": "string",
                        "description": "Document ID (for delete_document operation)",
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to scrape and ingest (for ingest operation)",
                    },
                    "file_content": {
                        "type": "string",
                        "description": "Base64-encoded file content (for ingest operation)",
                    },
                    "file_type": {
                        "type": "string",
                        "enum": ["pdf", "docx", "txt"],
                        "description": "Type of file (for ingest operation with file_content)",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadata for the document (for ingest operation)",
                    },
                    "chunk_size": {
                        "type": "integer",
                        "description": "Size of chunks for document ingestion",
                        "default": 1000,
                    },
                    "chunk_overlap": {
                        "type": "integer",
                        "description": "Overlap between chunks for document ingestion",
                        "default": 200,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (for query operation)",
                        "default": 5,
                    },
                },
                "required": ["operation"],
            },
        )
        self.vector_store = vector_store
        self.scraper_tool = ScraperTool()
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform RAG operations.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Result of the operation
        """
        operation = parameters.get("operation")
        collection_name = parameters.get("collection_name", "default")
        
        if operation == "query":
            return await self._handle_query(parameters)
        
        elif operation == "ingest":
            return await self._handle_ingest(parameters)
        
        elif operation == "list_collections":
            return await self._handle_list_collections()
        
        elif operation == "delete_document":
            return await self._handle_delete_document(parameters)
        
        elif operation == "delete_collection":
            return await self._handle_delete_collection(parameters)
        
        else:
            return {"error": f"Unknown operation: {operation}"}
    
    async def _handle_query(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle query operation.
        
        Args:
            parameters: Operation parameters
            
        Returns:
            Query results
        """
        query = parameters.get("query")
        if not query:
            return {"error": "Query parameter is required for query operation"}
        
        collection_name = parameters.get("collection_name", "default")
        limit = parameters.get("limit", 5)
        
        try:
            # Perform query
            results = await self.vector_store.search(
                query=query,
                collection_name=collection_name,
                limit=limit,
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "document": result.get("document", ""),
                    "metadata": result.get("metadata", {}),
                    "similarity": result.get("similarity", 0),
                })
            
            return {
                "results": formatted_results,
                "collection_name": collection_name,
                "query": query,
                "count": len(formatted_results),
            }
        
        except Exception as e:
            logger.exception(f"Error in RAG query: {e}")
            return {"error": f"Failed to query documents: {str(e)}"}
    
    async def _handle_ingest(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle ingest operation.
        
        Args:
            parameters: Operation parameters
            
        Returns:
            Ingestion results
        """
        collection_name = parameters.get("collection_name", "default")
        metadata = parameters.get("metadata", {})
        chunk_size = parameters.get("chunk_size", 1000)
        chunk_overlap = parameters.get("chunk_overlap", 200)
        
        # Check sources
        document = parameters.get("document")
        url = parameters.get("url")
        file_content = parameters.get("file_content")
        file_type = parameters.get("file_type")
        
        if not document and not url and not file_content:
            return {"error": "Either document, url, or file_content parameter is required for ingest operation"}
        
        try:
            # Process based on source
            if url:
                return await self._ingest_from_url(url, collection_name, metadata, chunk_size, chunk_overlap)
            
            elif file_content:
                if not file_type:
                    return {"error": "file_type parameter is required when using file_content"}
                
                return await self._ingest_from_file(file_content, file_type, collection_name, metadata, chunk_size, chunk_overlap)
            
            elif document:
                return await self._ingest_text(document, collection_name, metadata, chunk_size, chunk_overlap)
        
        except Exception as e:
            logger.exception(f"Error in RAG ingest: {e}")
            return {"error": f"Failed to ingest document: {str(e)}"}
    
    async def _handle_list_collections(self) -> Dict[str, Any]:
        """
        Handle list_collections operation.
        
        Returns:
            List of collections
        """
        try:
            collections = await self.vector_store.list_collections()
            
            return {
                "collections": collections,
                "count": len(collections),
            }
        
        except Exception as e:
            logger.exception(f"Error listing collections: {e}")
            return {"error": f"Failed to list collections: {str(e)}"}
    
    async def _handle_delete_document(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle delete_document operation.
        
        Args:
            parameters: Operation parameters
            
        Returns:
            Deletion result
        """
        document_id = parameters.get("document_id")
        if not document_id:
            return {"error": "document_id parameter is required for delete_document operation"}
        
        try:
            success = await self.vector_store.delete_document(document_id)
            
            return {
                "success": success,
                "document_id": document_id,
            }
        
        except Exception as e:
            logger.exception(f"Error deleting document: {e}")
            return {"error": f"Failed to delete document: {str(e)}"}
    
    async def _handle_delete_collection(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle delete_collection operation.
        
        Args:
            parameters: Operation parameters
            
        Returns:
            Deletion result
        """
        collection_name = parameters.get("collection_name")
        if not collection_name:
            return {"error": "collection_name parameter is required for delete_collection operation"}
        
        try:
            success = await self.vector_store.delete_collection(collection_name)
            
            return {
                "success": success,
                "collection_name": collection_name,
            }
        
        except Exception as e:
            logger.exception(f"Error deleting collection: {e}")
            return {"error": f"Failed to delete collection: {str(e)}"}
    
    async def _ingest_from_url(
        self,
        url: str,
        collection_name: str,
        metadata: Dict[str, Any],
        chunk_size: int,
        chunk_overlap: int,
    ) -> Dict[str, Any]:
        """
        Ingest content from a URL.
        
        Args:
            url: URL to scrape
            collection_name: Collection name
            metadata: Document metadata
            chunk_size: Size of chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Ingestion result
        """
        # Scrape the URL
        scraper_result = await self.scraper_tool.run({"url": url, "extract_type": "all"})
        
        if "error" in scraper_result:
            return {"error": f"Failed to scrape URL: {scraper_result['error']}"}
        
        # Get text content
        document = scraper_result.get("text", "")
        
        if not document:
            return {"error": "Failed to extract text from URL"}
        
        # Add metadata from scraping
        if "metadata" in scraper_result:
            url_metadata = scraper_result["metadata"]
            metadata.update({
                "source": "url",
                "url": url,
                "title": url_metadata.get("title", ""),
                "description": url_metadata.get("description", ""),
            })
        else:
            metadata.update({
                "source": "url",
                "url": url,
            })
        
        # Ingest the document
        return await self._ingest_text(document, collection_name, metadata, chunk_size, chunk_overlap)
    
    async def _ingest_from_file(
        self,
        file_content: str,
        file_type: str,
        collection_name: str,
        metadata: Dict[str, Any],
        chunk_size: int,
        chunk_overlap: int,
    ) -> Dict[str, Any]:
        """
        Ingest content from a file.
        
        Args:
            file_content: Base64-encoded file content
            file_type: File type (pdf, docx, txt)
            collection_name: Collection name
            metadata: Document metadata
            chunk_size: Size of chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Ingestion result
        """
        try:
            # Decode base64 content
            binary_content = base64.b64decode(file_content)
            
            # Extract text based on file type
            if file_type == "pdf":
                result = extract_text_from_pdf(file_content=binary_content)
                document = result.get("text", "")
                
                # Add metadata from PDF
                if "metadata" in result:
                    pdf_metadata = result["metadata"]
                    metadata.update({
                        "source": "pdf",
                        "title": pdf_metadata.get("title", ""),
                        "author": pdf_metadata.get("author", ""),
                        "page_count": pdf_metadata.get("page_count", 0),
                    })
                else:
                    metadata.update({"source": "pdf"})
            
            elif file_type == "docx":
                result = extract_text_from_docx(file_content=binary_content)
                document = result.get("text", "")
                
                # Add metadata from DOCX
                if "metadata" in result:
                    docx_metadata = result["metadata"]
                    metadata.update({
                        "source": "docx",
                        "title": docx_metadata.get("title", ""),
                        "author": docx_metadata.get("author", ""),
                    })
                else:
                    metadata.update({"source": "docx"})
            
            elif file_type == "txt":
                document = binary_content.decode("utf-8")
                metadata.update({"source": "txt"})
            
            else:
                return {"error": f"Unsupported file type: {file_type}"}
            
            if not document:
                return {"error": f"Failed to extract text from {file_type} file"}
            
            # Ingest the document
            return await self._ingest_text(document, collection_name, metadata, chunk_size, chunk_overlap)
        
        except Exception as e:
            logger.exception(f"Error processing file: {e}")
            return {"error": f"Failed to process file: {str(e)}"}
    
    async def _ingest_text(
        self,
        text: str,
        collection_name: str,
        metadata: Dict[str, Any],
        chunk_size: int,
        chunk_overlap: int,
    ) -> Dict[str, Any]:
        """
        Ingest text content.
        
        Args:
            text: Text to ingest
            collection_name: Collection name
            metadata: Document metadata
            chunk_size: Size of chunks
            chunk_overlap: Overlap between chunks
            
        Returns:
            Ingestion result
        """
        # Chunk the text if it's large
        if len(text) > chunk_size:
            chunks = chunk_text(text, chunk_size, chunk_overlap)
            
            # Ingest each chunk
            document_ids = []
            for i, chunk in enumerate(chunks):
                # Add chunk metadata
                chunk_metadata = metadata.copy()
                chunk_metadata.update({
                    "chunk_index": i,
                    "chunk_count": len(chunks),
                })
                
                # Ingest the chunk
                document_id = await self.vector_store.add_document(
                    document=chunk,
                    collection_name=collection_name,
                    metadata=chunk_metadata,
                )
                
                document_ids.append(document_id)
            
            return {
                "success": True,
                "document_ids": document_ids,
                "collection_name": collection_name,
                "chunk_count": len(chunks),
                "metadata": metadata,
            }
        
        else:
            # Ingest the whole document
            document_id = await self.vector_store.add_document(
                document=text,
                collection_name=collection_name,
                metadata=metadata,
            )
            
            return {
                "success": True,
                "document_id": document_id,
                "collection_name": collection_name,
                "metadata": metadata,
            }
