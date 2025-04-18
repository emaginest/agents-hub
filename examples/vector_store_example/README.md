# Vector Store Example

This example demonstrates how to use the PGVector tool from the Agents Hub framework to build a vector similarity search and retrieval system.

## Overview

The example shows how to:

1. Create a collection in PostgreSQL with pgvector
2. Add documents to the collection
3. Search for similar documents
4. Build a simple question-answering system using vector similarity search

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- OpenAI API key (for generating embeddings)

## Setup

### 1. Start PostgreSQL with pgvector

```bash
# From the vector_store_example directory
docker-compose up -d
```

This will start a PostgreSQL database with the pgvector extension installed and initialize the required tables.

### 2. Create a .env file

Create a `.env` file in the `vector_store_example` directory with your OpenAI API key:

```
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo  # or another model of your choice

# PostgreSQL connection parameters
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agents_hub
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

### 3. Install dependencies

Make sure you have the Agents Hub package installed:

```bash
# From the repository root
pip install -e .
```

## Running the Example

### Using environment variables

```bash
# From the vector_store_example directory
python vector_store_example.py
```

### Testing the fixed PGVector implementation

The PGVector class has been updated to fix connection issues. You can test the fix with:

```bash
# From the vector_store_example directory
python test_fix.py
```

### Alternative approaches

If you still encounter connection issues, you can try these alternative approaches:

#### Using direct connection parameters

```bash
# From the vector_store_example directory
python vector_store_direct.py
```

#### Debugging connection issues

If you're experiencing connection problems, run the debug script to diagnose the issue:

```bash
# From the vector_store_example directory
python debug_connection.py
```

## What's Happening

The example script:

1. Initializes an OpenAI LLM provider for generating embeddings
2. Creates a PGVector tool for interacting with PostgreSQL/pgvector
3. Creates an agent with the PGVector tool
4. Creates a collection for storing AI concepts
5. Adds several documents about AI concepts to the collection
6. Searches for documents similar to a query
7. Answers a question using the vector store
8. Lists all collections and counts documents

## How It Works

The PGVector tool:

1. Converts text to embeddings using the LLM provider
2. Stores embeddings in PostgreSQL with pgvector
3. Performs similarity searches using vector operations

## Customizing

You can modify the example to:

- Use a different LLM provider
- Add different documents
- Create multiple collections
- Implement more complex search patterns

## Cleaning Up

To stop and remove the PostgreSQL container:

```bash
# From the vector_store_example directory
docker-compose down -v
```
