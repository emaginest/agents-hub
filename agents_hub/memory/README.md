# Memory Module for Agents Hub

This module provides a sophisticated memory system for agents, enabling them to store, retrieve, and manage information across conversations and sessions.

## Components

### Memory Types

The memory system supports different types of memory:
- **Short-term Memory**: Recent conversation history
- **Long-term Memory**: Persistent knowledge and experiences
- **Episodic Memory**: Specific interactions and events
- **Semantic Memory**: General knowledge and concepts
- **Procedural Memory**: How to perform tasks and operations

### Memory Backends

The module supports multiple storage backends:
- **PostgreSQL**: For persistent, scalable storage
- **Redis**: For high-performance, in-memory storage
- **In-memory**: For testing and development
- **File-based**: For simple applications

### Memory Operations

The module provides operations for:
- **Storage**: Adding new memories
- **Retrieval**: Finding relevant memories
- **Forgetting**: Removing outdated or irrelevant memories
- **Consolidation**: Organizing and summarizing memories
- **Association**: Connecting related memories

## Usage

### Creating a Memory System

```python
from agents_hub.memory.backends import PostgreSQLMemory
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider (for embeddings)
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create PostgreSQL memory backend
memory = PostgreSQLMemory(
    llm=llm,  # For generating embeddings
    host="localhost",
    port=5432,
    database="agents_hub",
    user="postgres",
    password="postgres"
)

# Create agent with memory
from agents_hub import Agent

agent = Agent(
    name="memory_agent",
    llm=llm,
    memory=memory,
    system_prompt="You are an assistant that remembers past conversations."
)
```

### Storing and Retrieving Memories

```python
# Store a memory
await memory.store(
    agent_id="memory_agent",
    user_id="user123",
    content="The user is interested in quantum computing.",
    memory_type="semantic",
    metadata={"topic": "quantum computing", "importance": 0.8}
)

# Retrieve memories by semantic search
memories = await memory.retrieve(
    agent_id="memory_agent",
    user_id="user123",
    query="What topics is the user interested in?",
    limit=5
)

# Retrieve memories by metadata
memories = await memory.retrieve_by_metadata(
    agent_id="memory_agent",
    user_id="user123",
    metadata={"topic": "quantum computing"},
    limit=5
)
```

### Conversation History

```python
# Add message to conversation history
await memory.add_message(
    agent_id="memory_agent",
    user_id="user123",
    conversation_id="conv456",
    role="user",
    content="Tell me about quantum computing."
)

await memory.add_message(
    agent_id="memory_agent",
    user_id="user123",
    conversation_id="conv456",
    role="assistant",
    content="Quantum computing is a type of computation that harnesses quantum mechanical phenomena..."
)

# Get conversation history
history = await memory.get_conversation(
    conversation_id="conv456",
    limit=10
)

# Summarize conversation
summary = await memory.summarize_conversation(
    conversation_id="conv456",
    llm=llm
)
```

### Memory Management

```python
# Forget specific memories
await memory.forget(
    agent_id="memory_agent",
    user_id="user123",
    memory_ids=["mem123", "mem456"]
)

# Forget memories by criteria
await memory.forget_by_criteria(
    agent_id="memory_agent",
    user_id="user123",
    criteria={"topic": "outdated topic", "older_than": "30d"}
)

# Consolidate memories
await memory.consolidate(
    agent_id="memory_agent",
    user_id="user123",
    memory_type="episodic",
    strategy="summarize"
)
```

## Advanced Features

### Memory Hierarchies

```python
# Create a hierarchical memory system
from agents_hub.memory import HierarchicalMemory

hierarchical_memory = HierarchicalMemory(
    short_term=RedisMemory(...),
    long_term=PostgreSQLMemory(...),
    llm=llm
)

# Memory will automatically flow from short-term to long-term
# based on importance, recency, and frequency
```

### Memory Reflection

```python
# Reflect on memories to generate insights
insights = await memory.reflect(
    agent_id="memory_agent",
    user_id="user123",
    query="What patterns do you notice in our conversations?",
    llm=llm
)
```

### Memory Visualization

```python
# Generate a memory graph
graph_data = await memory.generate_graph(
    agent_id="memory_agent",
    user_id="user123",
    central_topic="quantum computing"
)

# Can be visualized with tools like D3.js or NetworkX
```

## Integration with Other Modules

The memory module integrates with:
- **Cognitive Module**: For reasoning about memories
- **RAG Module**: For enhancing retrieval with external knowledge
- **Monitoring**: For tracking memory usage and performance
