# PGVector Tool

The PGVector tool provides a flexible interface for working with PostgreSQL's pgvector extension, allowing users to build their own RAG (Retrieval-Augmented Generation) solutions.

## Overview

The PGVector tool enables:

- Vector similarity search in PostgreSQL
- Document storage and retrieval
- Collection management
- Building custom RAG systems

## Prerequisites

To use the PGVector tool, you need:

1. PostgreSQL database with the pgvector extension installed
2. Python dependencies: `psycopg2-binary`, `numpy`
3. An LLM provider for generating embeddings

## Installation

### PostgreSQL with pgvector

You can set up PostgreSQL with pgvector using Docker:

```bash
docker run -d \
  --name postgres-pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  pgvector/pgvector:latest
```

### Python Dependencies

Make sure you have the required dependencies:

```bash
pip install psycopg2-binary numpy
```

## Usage

### Initializing the Tool

```python
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import PGVectorTool

# Create LLM provider for embeddings
llm = OpenAIProvider(
    api_key="your-openai-api-key",
    model="gpt-3.5-turbo",
)

# Create PGVector tool
pgvector_tool = PGVectorTool(
    llm=llm,
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="postgres",
)
```

### Creating a Collection

```python
result = await pgvector_tool.run({
    "operation": "create_collection",
    "collection_name": "my_collection",
    "metadata": {"description": "My document collection"}
})
```

### Adding Documents

```python
# Add a single document
result = await pgvector_tool.run({
    "operation": "add_document",
    "collection_name": "my_collection",
    "document": "This is a sample document about artificial intelligence.",
    "metadata": {"source": "example", "category": "AI"}
})

# Add multiple documents
result = await pgvector_tool.run({
    "operation": "add_documents",
    "collection_name": "my_collection",
    "documents": [
        "Document 1 about machine learning.",
        "Document 2 about neural networks.",
        "Document 3 about deep learning."
    ],
    "metadata": {"source": "example", "category": "AI"}
})
```

### Searching for Similar Documents

```python
result = await pgvector_tool.run({
    "operation": "search",
    "collection_name": "my_collection",
    "query": "How does machine learning work?",
    "limit": 5
})
```

### Managing Collections

```python
# List all collections
result = await pgvector_tool.run({
    "operation": "list_collections"
})

# Count documents in a collection
result = await pgvector_tool.run({
    "operation": "count_documents",
    "collection_name": "my_collection"
})

# Delete a collection
result = await pgvector_tool.run({
    "operation": "delete_collection",
    "collection_name": "my_collection"
})
```

### Document Operations

```python
# Get a document by ID
result = await pgvector_tool.run({
    "operation": "get_document",
    "document_id": "document-uuid"
})

# Delete a document
result = await pgvector_tool.run({
    "operation": "delete_document",
    "document_id": "document-uuid"
})
```

## Building a RAG System

You can build a complete RAG system using the PGVector tool:

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import PGVectorTool, ScraperTool

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create tools
pgvector_tool = PGVectorTool(llm=llm)
scraper_tool = ScraperTool()

# Create RAG agent
rag_agent = Agent(
    name="rag_agent",
    llm=llm,
    tools=[pgvector_tool, scraper_tool],
    system_prompt="""You are a knowledge management assistant.
    Use the pgvector tool to store and retrieve information.
    When answering questions, first search for relevant information,
    then use that information to formulate your response.""",
)

# Use the agent
response = await rag_agent.run(
    "What is machine learning? Search the 'ai_concepts' collection for information."
)
```

## Advanced Configuration

### Chunking Options

When adding documents, you can configure how they are chunked:

```python
result = await pgvector_tool.run({
    "operation": "add_document",
    "collection_name": "my_collection",
    "document": "Long document text...",
    "chunk_size": 1000,  # Maximum size of each chunk
    "chunk_overlap": 200,  # Overlap between chunks
    "chunk_method": "sentence"  # Options: token, character, sentence
})
```

### Custom Schema

You can specify a custom PostgreSQL schema:

```python
pgvector_tool = PGVectorTool(
    llm=llm,
    host="localhost",
    schema="my_schema",  # Default is "public"
)
```

### Custom Embedding Dimension

If you're using embeddings with a different dimension:

```python
pgvector_tool = PGVectorTool(
    llm=llm,
    embedding_dimension=384,  # Default is 1536 for OpenAI embeddings
)
```

## Error Handling

The tool returns errors in a consistent format:

```python
result = await pgvector_tool.run({...})
if "error" in result:
    print(f"Error: {result['error']}")
else:
    # Process successful result
    print(result)
```

## Performance Considerations

- For large collections, consider adding additional indexes to the PostgreSQL database
- When adding many documents, use the `add_documents` operation instead of multiple `add_document` calls
- Adjust chunk size based on your specific use case and embedding model

## Example

See the complete example in `examples/tools/pgvector_example.py`.
