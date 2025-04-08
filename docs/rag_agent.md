# RAG Agent

The RAGAgent is a specialized agent for Retrieval-Augmented Generation (RAG) that combines the PGVector and Scraper tools to provide a complete solution for knowledge management.

## Overview

The RAGAgent provides a high-level interface for:

- Scraping and storing content from URLs
- Querying the knowledge base
- Managing collections of documents
- Answering questions based on retrieved information

## Prerequisites

To use the RAGAgent, you need:

1. PostgreSQL database with the pgvector extension installed
2. OpenAI API key or another LLM provider
3. Python dependencies: `psycopg2-binary`, `pgvector`

## Installation

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

## Basic Usage

```python
import asyncio
from agents_hub import RAGAgent
from agents_hub.llm.providers import OpenAIProvider

async def main():
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
    result = await rag_agent.scrape_and_store(
        url="https://en.wikipedia.org/wiki/Retrieval-augmented_generation",
        collection_name="my_collection",
    )
    print(f"Scraped and stored content from URL")
    
    # Answer a question
    question = "What is retrieval-augmented generation?"
    answer_result = await rag_agent.answer_question(question, "my_collection")
    print(f"Question: {question}")
    print(f"Answer: {answer_result['answer']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

### Customizing Chunking Parameters

```python
rag_agent = RAGAgent(
    llm=llm,
    chunk_size=500,  # Smaller chunks
    chunk_overlap=100,  # Less overlap
    chunk_method="token",  # Use token-based chunking
)
```

### Custom System Prompt

```python
rag_agent = RAGAgent(
    llm=llm,
    system_prompt="""You are a specialized RAG assistant focused on scientific information.
    When answering questions, prioritize accuracy and cite sources when possible.
    If you're uncertain, acknowledge the limitations of the available information.""",
)
```

### Working with Multiple Collections

```python
# Create collections for different topics
await rag_agent.create_collection("science")
await rag_agent.create_collection("history")

# Scrape and store content in different collections
await rag_agent.scrape_and_store(
    url="https://en.wikipedia.org/wiki/Physics",
    collection_name="science",
)
await rag_agent.scrape_and_store(
    url="https://en.wikipedia.org/wiki/World_War_II",
    collection_name="history",
)

# Answer questions from specific collections
science_answer = await rag_agent.answer_question(
    "What is quantum mechanics?",
    collection_name="science",
)
history_answer = await rag_agent.answer_question(
    "When did World War II end?",
    collection_name="history",
)
```

## API Reference

### Constructor

```python
RAGAgent(
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
)
```

### Collection Management

#### create_collection

```python
async def create_collection(
    collection_name: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]
```

Creates a new collection in the vector database.

#### list_collections

```python
async def list_collections() -> Dict[str, Any]
```

Lists all collections in the vector database.

#### delete_collection

```python
async def delete_collection(collection_name: str) -> Dict[str, Any]
```

Deletes a collection from the vector database.

#### count_documents

```python
async def count_documents(collection_name: str) -> Dict[str, Any]
```

Counts documents in a collection.

### Content Management

#### scrape_url

```python
async def scrape_url(
    url: str,
    extract_type: str = "text",
) -> Dict[str, Any]
```

Scrapes content from a URL.

#### store_document

```python
async def store_document(
    document: str,
    collection_name: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]
```

Stores a document in the vector database.

#### scrape_and_store

```python
async def scrape_and_store(
    url: str,
    collection_name: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]
```

Scrapes content from a URL and stores it in the vector database.

### Querying

#### search

```python
async def search(
    query: str,
    collection_name: str,
    limit: Optional[int] = None,
) -> Dict[str, Any]
```

Searches for documents in the vector database.

#### answer_question

```python
async def answer_question(
    question: str,
    collection_name: str,
    limit: Optional[int] = None,
) -> Dict[str, Any]
```

Answers a question using the RAG approach.

#### chat

```python
async def chat(message: str) -> str
```

Chats with the agent directly.

## Error Handling

The RAGAgent includes comprehensive error handling for all operations. Errors are returned in a consistent format:

```python
{
    "error": "Error message"
}
```

You can check for errors in the result:

```python
result = await rag_agent.scrape_and_store(url, collection_name)
if "error" in result:
    print(f"Error: {result['error']}")
else:
    print("Success!")
```

## Performance Considerations

- For large collections, consider adding additional indexes to the PostgreSQL database
- Adjust chunk size based on your specific use case and embedding model
- For very large documents, consider processing them in batches

## Examples

See the complete example in `examples/rag/` for a full implementation of a RAG system with a web interface.
