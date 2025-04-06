# Agents Hub Examples

This directory contains example applications and usage patterns for the Agents Hub framework.

## Contents

### FastAPI Application

The `fastapi_app` directory contains a complete FastAPI application that demonstrates how to integrate Agents Hub into a web service.

To run the FastAPI example:

```bash
cd fastapi_app
python main.py
```

The API will be available at http://localhost:8000, with documentation at http://localhost:8000/docs.

### Agent Workforce

The `agent_workforce` directory contains examples of creating and using agent workforces:

- `simple_workforce.py`: Demonstrates creating a basic workforce with specialized agents

To run the agent workforce example:

```bash
cd agent_workforce
python simple_workforce.py
```

## Creating Your Own Examples

Feel free to create your own examples in this directory. Some ideas:

1. **Custom Agent Implementation**: Create a specialized agent for a specific domain
2. **Tool Integration**: Demonstrate how to create and use custom tools
3. **Memory System**: Show how to use different memory backends
4. **RAG Integration**: Implement a domain-specific RAG system

## Docker Support

You can also run the examples using Docker:

```bash
cd ../docker
docker-compose up -d
```

This will start:
- PostgreSQL with pgvector extension
- Ollama for local LLM inference
- FastAPI example application
