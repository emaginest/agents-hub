import uvicorn
import logging
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from app.routes import rag, aria, health
from app.config import Settings
from app.core.memory import memory

settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Add any async startup code here
    try:
        yield
    finally:
        # Shutdown: Clean up resources
        # Note: DynamoDB doesn't need explicit connection cleanup
        print("Shutting down application...")


app = FastAPI(
    title="ARIA - Maternal Health Assistant",
    version="1.0.0",
    description="AI-powered maternal health assistant with RAG capabilities and DynamoDB memory",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


# Include routers
app.include_router(rag.router, prefix="/api/v1/rag", tags=["rag"])
app.include_router(aria.router, prefix="/api/v1/aria", tags=["aria"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
    )
