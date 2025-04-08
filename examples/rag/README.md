# RAG Example with RAGAgent

This example demonstrates how to build a Retrieval-Augmented Generation (RAG) system using the RAGAgent from the agents-hub framework.

## Overview

The RAG system allows you to:

1. Scrape content from URLs and store it in a vector database
2. Query the knowledge base to retrieve relevant information
3. Answer questions based on the retrieved information
4. Manage collections of documents

## Architecture

The example consists of the following components:

- **RAGAgent**: A specialized agent from the agents-hub framework that provides high-level RAG functionality
- **FastAPI Application**: API endpoints for scraping, querying, and managing collections
- **Web Interface**: A simple interface for interacting with the RAG system
- **PostgreSQL with pgvector**: Vector database for storing and retrieving documents

## Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension
- OpenAI API key

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up environment variables

Copy the `.env.example` file to `.env` and fill in your OpenAI API key:

```bash
cp .env.example .env
```

Edit the `.env` file:

```
OPENAI_API_KEY=your-openai-api-key
```

### 3. Start PostgreSQL with pgvector

You can use Docker to run PostgreSQL with pgvector:

```bash
docker-compose up -d postgres
```

### 4. Run the application

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --reload
```

### 5. Access the web interface

Open your browser and navigate to:

```
http://localhost:8000
```

## Using the RAG System

### 1. Create a Collection

First, create a collection to store your documents:

1. Enter a collection name in the "Collections" section
2. Click "Create"

### 2. Scrape and Store Content

To add content to your collection:

1. Enter a URL in the "Scrape URL" section
2. Select the collection you created
3. Click "Scrape and Store"

### 3. Query the Knowledge Base

To ask questions about the stored content:

1. Enter your question in the "Query Knowledge Base" section
2. Select the collection to search
3. Click "Ask Question"

The system will:
- Search for relevant documents in the collection
- Generate an answer based on the retrieved documents
- Display the answer and the sources used

## API Endpoints

The application provides the following API endpoints:

### Collections

- `GET /api/collections`: List all collections
- `POST /api/collections`: Create a new collection
- `DELETE /api/collections/{collection_name}`: Delete a collection
- `GET /api/collections/{collection_name}/count`: Count documents in a collection

### Scraping and Querying

- `POST /api/scrape`: Scrape content from a URL and store it
- `POST /api/query`: Answer a question using the RAG approach
- `POST /api/chat`: Chat with the agent directly

### Health Check

- `GET /api/health`: Health check endpoint

## Docker Deployment

You can deploy the entire application using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL with pgvector
- The FastAPI application

## Customization

You can customize the RAG system by modifying the following:

### Document Processing

Adjust the chunking parameters in the `.env` file:

```
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHUNK_METHOD=sentence
```

### Search Limit

Change the maximum number of results to return when searching:

```
SEARCH_LIMIT=5
```

### LLM Model

Change the OpenAI model used for embeddings and responses:

```
OPENAI_MODEL=gpt-4
```

## Implementation Details

### RAG Agent (agent.py)

The `RAGAgent` class provides:
- Methods for scraping and storing content
- Methods for querying the knowledge base
- Methods for managing collections

### FastAPI Application (app.py)

The FastAPI application provides:
- API endpoints for the RAG system
- A simple web interface
- Error handling and logging

### Web Interface (static/)

The web interface provides:
- A form for creating and managing collections
- A form for scraping URLs
- A form for querying the knowledge base
- Display of answers and sources

## Extending the Example

You can extend this example in several ways:

1. **Add Authentication**: Implement user authentication for the API
2. **Support More Document Types**: Add support for PDFs, DOCXs, etc.
3. **Implement Streaming Responses**: Use streaming for long-running operations
4. **Add Visualization**: Visualize the vector embeddings
5. **Implement Chat History**: Store and display chat history

## Troubleshooting

### PostgreSQL Connection Issues

If you have issues connecting to PostgreSQL:

1. Check that PostgreSQL is running: `docker ps`
2. Verify the connection parameters in the `.env` file
3. Ensure the pgvector extension is installed

### OpenAI API Issues

If you have issues with the OpenAI API:

1. Verify your API key in the `.env` file
2. Check your OpenAI API usage and limits
3. Try a different model

## License

This example is part of the agents-hub framework and is licensed under the MIT License.
