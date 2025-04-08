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
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, HttpUrl

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from agents_hub.llm.providers import OpenAIProvider
from agents_hub import RAGAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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

# Initialize RAG agent
rag_agent = RAGAgent(
    llm=llm,
    pg_host=os.environ.get("POSTGRES_HOST", "localhost"),
    pg_port=int(os.environ.get("POSTGRES_PORT", "5432")),
    pg_database=os.environ.get("POSTGRES_DB", "postgres"),
    pg_user=os.environ.get("POSTGRES_USER", "postgres"),
    pg_password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
    chunk_size=int(os.environ.get("CHUNK_SIZE", "1000")),
    chunk_overlap=int(os.environ.get("CHUNK_OVERLAP", "200")),
    chunk_method=os.environ.get("CHUNK_METHOD", "sentence"),
    search_limit=int(os.environ.get("SEARCH_LIMIT", "5")),
)


# Define request and response models
class CollectionCreate(BaseModel):
    name: str = Field(..., description="Name of the collection")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the collection")


class ScrapeRequest(BaseModel):
    url: HttpUrl = Field(..., description="URL to scrape")
    collection_name: str = Field(..., description="Name of the collection to store the content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional metadata for the document")


class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to answer")
    collection_name: str = Field(..., description="Name of the collection to search")
    limit: Optional[int] = Field(None, description="Maximum number of results to return")


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
        result = await rag_agent.list_collections()
        return result
    except Exception as e:
        logger.exception("Error listing collections")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/collections", response_model=Dict[str, Any])
async def create_collection(collection: CollectionCreate):
    """Create a new collection."""
    try:
        result = await rag_agent.create_collection(collection.name, collection.metadata)
        return result
    except Exception as e:
        logger.exception("Error creating collection")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/collections/{collection_name}", response_model=Dict[str, Any])
async def delete_collection(collection_name: str):
    """Delete a collection."""
    try:
        result = await rag_agent.delete_collection(collection_name)
        return result
    except Exception as e:
        logger.exception("Error deleting collection")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/collections/{collection_name}/count", response_model=Dict[str, Any])
async def count_documents(collection_name: str):
    """Count documents in a collection."""
    try:
        result = await rag_agent.count_documents(collection_name)
        return result
    except Exception as e:
        logger.exception("Error counting documents")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scrape", response_model=Dict[str, Any])
async def scrape_url(request: ScrapeRequest):
    """Scrape content from a URL and store it in the vector database."""
    try:
        result = await rag_agent.scrape_and_store(
            url=str(request.url),
            collection_name=request.collection_name,
            metadata=request.metadata,
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error scraping URL")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=Dict[str, Any])
async def query(request: QueryRequest):
    """Answer a question using the RAG approach."""
    try:
        result = await rag_agent.answer_question(
            question=request.question,
            collection_name=request.collection_name,
            limit=request.limit,
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error answering question")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=Dict[str, str])
async def chat(request: ChatRequest):
    """Chat with the agent directly."""
    try:
        response = await rag_agent.chat(request.message)
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
