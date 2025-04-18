"""
RAG FastAPI Application

This module implements a FastAPI application that provides endpoints for:
- Scraping and storing content from URLs
- Querying the knowledge base
- Managing collections
- Serving a simple web interface
"""

import os
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from agents_hub.llm.providers import OpenAIProvider
from agents_hub import Agent
from agents_hub.vector_stores import PGVector
from agents_hub.tools.standard import ScraperTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG API",
    description="API for Retrieval-Augmented Generation using agents-hub",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="static")

# Initialize LLM provider
llm = OpenAIProvider(
    api_key=os.environ["OPENAI_API_KEY"],
    model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
)

# Initialize tools
pgvector_tool = PGVector(
    llm=llm,
    host=os.environ.get("POSTGRES_HOST", "localhost"),
    port=int(os.environ.get("POSTGRES_PORT", "5432")),
    database=os.environ.get("POSTGRES_DB", "postgres"),
    user=os.environ.get("POSTGRES_USER", "postgres"),
    password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
)

scraper_tool = ScraperTool()

# Configuration for chunking
chunk_size = int(os.environ.get("CHUNK_SIZE", "1000"))
chunk_overlap = int(os.environ.get("CHUNK_OVERLAP", "200"))
chunk_method = os.environ.get("CHUNK_METHOD", "sentence")
search_limit = int(os.environ.get("SEARCH_LIMIT", "5"))

# Initialize RAG agent using core components
rag_agent = Agent(
    name="rag_agent",
    llm=llm,
    tools=[pgvector_tool, scraper_tool],
    system_prompt="""You are a knowledge management assistant specialized in Retrieval-Augmented Generation (RAG).

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
    """,
)


# Define request and response models
class CollectionCreate(BaseModel):
    name: str = Field(..., description="Name of the collection")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata for the collection"
    )


class ScrapeRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL to scrape")
    collection_name: str = Field(
        ..., description="Name of the collection to store the content"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Optional metadata for the document"
    )


class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to answer")
    collection_name: str = Field(..., description="Name of the collection to search")
    limit: Optional[int] = Field(
        None, description="Maximum number of results to return"
    )


class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")


# Define API endpoints
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the web interface."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/collections", response_model=Dict[str, Any])
async def list_collections():
    """List all collections."""
    try:
        result = await pgvector_tool.run({"operation": "list_collections"})
        return result
    except Exception as e:
        logger.exception("Error listing collections")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/collections", response_model=Dict[str, Any])
async def create_collection(collection: CollectionCreate):
    """Create a new collection."""
    try:
        result = await pgvector_tool.run(
            {
                "operation": "create_collection",
                "collection_name": collection.name,
                "metadata": collection.metadata or {},
            }
        )
        return result
    except Exception as e:
        logger.exception("Error creating collection")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/collections/{collection_name}", response_model=Dict[str, Any])
async def delete_collection(collection_name: str):
    """Delete a collection."""
    try:
        result = await pgvector_tool.run(
            {"operation": "delete_collection", "collection_name": collection_name}
        )
        return result
    except Exception as e:
        logger.exception("Error deleting collection")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/collections/{collection_name}/count", response_model=Dict[str, Any])
async def count_documents(collection_name: str):
    """Count documents in a collection."""
    try:
        result = await pgvector_tool.run(
            {"operation": "count_documents", "collection_name": collection_name}
        )
        return result
    except Exception as e:
        logger.exception("Error counting documents")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scrape", response_model=Dict[str, Any])
async def scrape_url(request: ScrapeRequest):
    """Scrape content from a URL and store it in the vector database."""
    try:
        # Step 1: Scrape the URL
        scrape_result = await scraper_tool.run(
            {"url": str(request.url), "extract_type": "all"}
        )

        if "error" in scrape_result:
            raise HTTPException(status_code=400, detail=scrape_result["error"])

        # Extract text content
        text = scrape_result.get("text", "")

        if not text:
            logger.warning(f"No text content found in URL: {request.url}")
            raise HTTPException(
                status_code=400, detail="No text content found in the URL"
            )

        # Prepare metadata
        doc_metadata = {
            "source": str(request.url),
            "title": scrape_result.get("metadata", {}).get("title", ""),
            "description": scrape_result.get("metadata", {}).get("description", ""),
        }

        # Add additional metadata if provided
        if request.metadata:
            doc_metadata.update(request.metadata)

        # Step 2: Store the document
        store_result = await pgvector_tool.run(
            {
                "operation": "add_document",
                "document": text,
                "collection_name": request.collection_name,
                "metadata": doc_metadata,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "chunk_method": chunk_method,
            }
        )

        return {
            "scrape_result": scrape_result,
            "store_result": store_result,
            "url": str(request.url),
            "collection_name": request.collection_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error scraping URL")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=Dict[str, Any])
async def query(request: QueryRequest):
    """Answer a question using the RAG approach."""
    try:
        # Step 1: Search for relevant documents
        search_result = await pgvector_tool.run(
            {
                "operation": "search",
                "query": request.question,
                "collection_name": request.collection_name,
                "limit": request.limit or search_limit,
            }
        )

        if "error" in search_result:
            raise HTTPException(status_code=400, detail=search_result["error"])

        # Extract search results
        results = search_result.get("results", [])

        if not results:
            logger.warning(
                f"No relevant documents found for question: {request.question}"
            )
            return {
                "answer": "I don't have enough information to answer this question.",
                "search_results": [],
                "question": request.question,
                "collection_name": request.collection_name,
            }

        # Prepare context from search results
        context = "\n\n".join(
            [
                f"Document {i+1}:\n{result['document']}"
                for i, result in enumerate(results)
            ]
        )

        # Generate answer using the agent
        prompt = f"""
        Question: {request.question}

        Please answer the question based on the following information:

        {context}

        Answer:
        """

        response = await rag_agent.run(prompt)

        return {
            "answer": response,
            "search_results": results,
            "question": request.question,
            "collection_name": request.collection_name,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error answering question")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=Dict[str, str])
async def chat(request: ChatRequest):
    """Chat with the agent directly."""
    try:
        response = await rag_agent.run(request.message)
        return {"response": response}
    except Exception as e:
        logger.exception("Error in chat")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


def start():
    """Start the FastAPI application."""
    uvicorn.run(
        "app:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
        reload=True,
    )


if __name__ == "__main__":
    start()
