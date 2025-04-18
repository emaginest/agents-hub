"""
Example demonstrating how to use the recursive character text splitter with PGVector for RAG.

This example shows how to:
1. Process a document with the recursive character text splitter
2. Store the chunks in a PGVector collection
3. Perform a similarity search to retrieve relevant chunks
4. Answer questions based on the retrieved chunks
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.vector_stores import PGVector
from agents_hub.utils.document import chunk_text

# Load environment variables
load_dotenv()

# Sample document with structured content (markdown-like)
SAMPLE_DOCUMENT = """
# Recursive Character Text Splitter

## Introduction

The recursive character text splitter is a powerful tool for splitting documents into chunks
while respecting the document's structure. It works by recursively applying a list of separators
to split the text into increasingly smaller chunks until they meet the desired size constraints.

## How It Works

The recursive character text splitter uses a list of separators in order of priority:
1. First, it tries to split on the highest priority separator (e.g., paragraph breaks)
2. If the resulting chunks are still too large, it tries the next separator
3. This process continues until all chunks are within the specified size limit
4. If no separators work, it falls back to character-based chunking

## Benefits

### Structure Preservation

Unlike simple character or token-based chunking, the recursive approach preserves the
document's logical structure. This is especially important for:
- Technical documentation
- Markdown files
- Code with comments
- Legal documents

### Semantic Coherence

By respecting document structure, the recursive splitter helps maintain semantic coherence
within chunks. This improves:
- Retrieval quality in RAG systems
- Context understanding for LLMs
- Answer generation based on retrieved chunks

## Usage Examples

### Basic Usage

```python
from agents_hub.utils.document import chunk_text

chunks = chunk_text(
    text=document_text,
    chunk_size=1000,
    chunk_overlap=200,
    chunk_method="recursive"
)
```

### Custom Separators

```python
chunks = chunk_text(
    text=document_text,
    chunk_size=1000,
    chunk_overlap=200,
    chunk_method="recursive",
    separators=["## ", "\\n\\n", "\\n", ". ", " "]
)
```

## Implementation Details

The recursive character text splitter is implemented in the `agents_hub.utils.document.chunking`
module. The implementation uses a depth-first recursive approach to split the text efficiently.

## Conclusion

The recursive character text splitter provides a more intelligent way to chunk documents
for RAG systems and other NLP applications. By respecting document structure, it improves
the quality of downstream tasks like retrieval and question answering.
"""


async def main():
    # Initialize OpenAI provider for embeddings and completions
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    llm = OpenAIProvider(api_key=api_key)
    
    # Initialize PGVector
    pg_vector = PGVector(
        llm=llm,
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        database=os.getenv("POSTGRES_DB", "agents_hub"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres")
    )
    
    # Create an agent with the PGVector tool
    agent = Agent(
        name="rag_agent",
        llm=llm,
        tools=[pg_vector],
        system_prompt="You are a helpful assistant with access to a vector database. Use the PGVector tool to retrieve relevant information before answering questions."
    )
    
    # Create a collection
    collection_name = "recursive_chunking_docs"
    print(f"Creating collection: {collection_name}")
    await pg_vector.create_collection(collection_name)
    
    # Process the document with recursive character chunking
    print("Processing document with recursive character chunking...")
    
    # Define custom separators for markdown-like content
    custom_separators = ["## ", "\n\n", "\n", ". ", " "]
    
    chunks = chunk_text(
        text=SAMPLE_DOCUMENT,
        chunk_size=300,  # Smaller chunks for demonstration
        chunk_overlap=50,
        chunk_method="recursive",
        separators=custom_separators
    )
    
    print(f"Document split into {len(chunks)} chunks")
    
    # Store chunks in the vector database
    print("Storing chunks in vector database...")
    for i, chunk in enumerate(chunks):
        await pg_vector.add_document(
            collection_name=collection_name,
            text=chunk,
            metadata={
                "source": "recursive_chunking_doc",
                "chunk_id": i,
                "chunk_method": "recursive"
            }
        )
    
    # Perform a similarity search
    print("\nPerforming similarity search...")
    search_query = "How does the recursive character text splitter preserve document structure?"
    search_results = await pg_vector.search(
        collection_name=collection_name,
        query=search_query,
        limit=3
    )
    
    print(f"Search query: {search_query}")
    print(f"Found {len(search_results)} results:")
    for i, result in enumerate(search_results):
        print(f"\nResult {i+1} (score: {result['score']:.4f}):")
        print(f"Text: {result['text'][:150]}...")
    
    # Answer a question using the agent with PGVector
    print("\nAnswering question using RAG...")
    question = "What are the benefits of using the recursive character text splitter compared to simple chunking methods?"
    answer = await agent.run(f"Use the PGVector tool to search the '{collection_name}' collection and answer this question: {question}")
    
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    
    # Clean up
    print("\nCleaning up...")
    await pg_vector.delete_collection(collection_name)
    print(f"Collection '{collection_name}' deleted")


if __name__ == "__main__":
    asyncio.run(main())
