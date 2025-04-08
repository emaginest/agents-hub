# FastAPI Example for Agents Hub

This example demonstrates how to use the Agents Hub framework in a FastAPI application. It provides a REST API for interacting with agents, RAG capabilities, and other features of the framework.

## Features

- REST API for agent interactions
- PostgreSQL with pgvector for RAG functionality
- Ollama integration for local LLM support
- Environment variable configuration
- Docker support for easy deployment

## Running with Docker

The easiest way to run this example is using Docker Compose, which sets up:
- PostgreSQL with pgvector extension
- Ollama for local LLM support
- The FastAPI application

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Steps

1. **Create a `.env` file** (optional) with your API keys:
   ```
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   GOOGLE_API_KEY=your-google-api-key
   ```

2. **Start the services**:
   ```bash
   cd examples/fastapi_app
   docker-compose up -d
   ```

3. **Access the API**:
   - API documentation: http://localhost:8000/docs
   - API endpoints: http://localhost:8000/api/v1/...

4. **Stop the services**:
   ```bash
   docker-compose down
   ```

## Running Locally

If you prefer to run the application without Docker:

### Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension
- (Optional) Ollama for local LLM support

### Steps

1. **Install dependencies**:
   ```bash
   pip install -e ../../  # Install agents-hub
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   export POSTGRES_HOST=localhost
   export POSTGRES_PORT=5432
   export POSTGRES_DB=agents_hub
   export POSTGRES_USER=postgres
   export POSTGRES_PASSWORD=postgres
   export OPENAI_API_KEY=your-openai-api-key
   # Add other API keys as needed
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## API Endpoints

- `/api/v1/agents` - List available agents
- `/api/v1/agents/{agent_id}/run` - Run an agent with a prompt
- `/api/v1/rag/collections` - Manage RAG collections
- `/api/v1/rag/documents` - Add documents to collections
- `/api/v1/rag/search` - Search for documents
- `/api/v1/rag/answer` - Answer questions using RAG

## Configuration

The application can be configured using environment variables:

- `POSTGRES_HOST` - PostgreSQL host (default: localhost)
- `POSTGRES_PORT` - PostgreSQL port (default: 5432)
- `POSTGRES_DB` - PostgreSQL database name (default: agents_hub)
- `POSTGRES_USER` - PostgreSQL username (default: postgres)
- `POSTGRES_PASSWORD` - PostgreSQL password (default: postgres)
- `OLLAMA_BASE_URL` - Ollama base URL (default: http://localhost:11434)
- `OLLAMA_MODEL` - Ollama model to use (default: llama3)
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `GOOGLE_API_KEY` - Google API key

## Docker Compose Services

The `docker-compose.yml` file sets up three services:

1. **postgres** - PostgreSQL database with pgvector extension
   - Port: 5432
   - Credentials: postgres/postgres
   - Database: agents_hub
   - Initialized with schema for RAG and memory

2. **ollama** - Ollama for local LLM support
   - Port: 11434
   - GPU support enabled (if available)

3. **api** - FastAPI application
   - Port: 8000
   - Connected to PostgreSQL and Ollama
   - Mounts the project directory for development
