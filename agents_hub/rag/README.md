# RAG Module for Agents Hub

This module provides Retrieval-Augmented Generation (RAG) capabilities for the Agents Hub framework, allowing agents to access and leverage external knowledge.

## Components

### RAG Agent

The RAGAgent is a specialized agent that can:
- Create and manage vector collections
- Scrape and store content from websites
- Process and chunk documents
- Generate embeddings for text
- Perform semantic searches
- Answer questions using retrieved context

### Vector Stores

The module supports multiple vector store backends:
- **PostgreSQL/pgvector**: Efficient vector storage and retrieval
- **In-memory**: For testing and development
- **Redis**: For high-performance applications

## Usage

### Creating a RAG Agent

```python
from agents_hub import RAGAgent
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create RAG agent with PostgreSQL vector store
rag_agent = RAGAgent(
    llm=llm,
    pg_host="localhost",
    pg_port=5432,
    pg_database="postgres",
    pg_user="postgres",
    pg_password="postgres"
)

# Create a collection
await rag_agent.create_collection("research")
```

### Adding Content to Collections

```python
# Scrape and store content from a URL
await rag_agent.scrape_and_store(
    url="https://example.com/article",
    collection_name="research"
)

# Add document from text
await rag_agent.add_document(
    text="This is a sample document about artificial intelligence.",
    metadata={"source": "manual", "topic": "AI"},
    collection_name="research"
)

# Process and add content from a PDF
from agents_hub.utils.document import extract_text_from_pdf

pdf_result = extract_text_from_pdf("document.pdf")
await rag_agent.add_document(
    text=pdf_result["text"],
    metadata=pdf_result["metadata"],
    collection_name="research"
)
```

### Searching and Retrieving Information

```python
# Search for relevant documents
search_results = await rag_agent.search(
    query="What are the latest developments in AI?",
    collection_name="research",
    limit=5
)

# Answer a question using RAG
answer = await rag_agent.answer_question(
    question="What are the key benefits of quantum computing?",
    collection_name="research"
)

print(answer["answer"])
print(answer["sources"])
```

### Managing Collections

```python
# List all collections
collections = await rag_agent.list_collections()

# Get collection statistics
stats = await rag_agent.get_collection_stats("research")

# Delete a collection
await rag_agent.delete_collection("research")
```

## Advanced Features

### Custom Chunking Strategies

```python
from agents_hub.utils.document import chunk_text

# Custom chunking
chunks = chunk_text(
    text=long_document,
    chunk_size=1000,
    chunk_overlap=200,
    chunk_method="sentence"  # Options: token, character, sentence, recursive
)

# Recursive character chunking with custom separators
chunks = chunk_text(
    text=long_document,
    chunk_size=1000,
    chunk_overlap=200,
    chunk_method="recursive",
    separators=["## ", "\n\n", "\n", ". ", " "]  # Custom separators in order of priority
)

# Add chunks to collection
for i, chunk in enumerate(chunks):
    await rag_agent.add_document(
        text=chunk,
        metadata={"source": "document.pdf", "chunk": i},
        collection_name="research"
    )
```

### Hybrid Search

```python
# Perform hybrid search (combining semantic and keyword search)
results = await rag_agent.search(
    query="quantum computing applications",
    collection_name="research",
    search_type="hybrid",
    keyword_weight=0.3,  # 30% keyword, 70% semantic
    limit=10
)
```

### Integration with Cognitive Agents

```python
from agents_hub import CognitiveAgent
from agents_hub.cognitive import CognitiveArchitecture

# Create cognitive architecture
cognitive_architecture = CognitiveArchitecture()

# Create cognitive agent with RAG capabilities
agent = CognitiveAgent(
    name="knowledge_agent",
    llm=llm,
    cognitive_architecture=cognitive_architecture,
    tools=[rag_agent],
    system_prompt="You are a knowledgeable assistant that can retrieve and reason with information."
)

# Use the agent to answer questions with RAG
response = await agent.run(
    "Explain the implications of quantum computing for cryptography.",
    context={"reasoning_mechanism": "deductive"}
)
```

## Performance Optimization

The RAG module includes several performance optimizations:
- Batched embedding generation
- Caching of frequently accessed embeddings
- Parallel processing of documents
- Optimized PostgreSQL queries with indexes
