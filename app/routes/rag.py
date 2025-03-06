from fastapi import APIRouter, HTTPException
from app.models.schema import QueryRequest, QueryResponse, DocumentInput
from app.core.retrieval import retrieve_context, ingest_document
from app.utils.scraper import scrape_urls
from app.core.generation import generate_response

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        context = await retrieve_context(request.query, request.collection_name)
        answer = await generate_response(request.query, context)
        return QueryResponse(answer=answer, sources=context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest")
async def ingest_urls(document: DocumentInput):
    """
    Ingest content from URLs into the vector store.

    Args:
        document: DocumentInput containing list of URLs and optional collection name
    """
    try:
        # Scrape content from URLs
        scraped_contents = await scrape_urls(document.urls)

        # Ingest each document
        for text, metadata in scraped_contents:
            await ingest_document(
                text=text, metadata=metadata, collection_name=document.collection_name
            )

        return {
            "status": "success",
            "message": f"Successfully ingested {len(scraped_contents)} documents",
            "urls": document.urls,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "RAG system is operational"}
