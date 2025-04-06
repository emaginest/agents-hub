"""
Example of using the RAG tool in the Agents Hub framework.
"""

import os
import asyncio
import base64
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.tools.standard import RAGTool
from agents_hub.knowledge.rag.backends.postgres import PostgreSQLVectorStorage


async def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if PostgreSQL is configured
    if not all([
        os.environ.get("POSTGRES_HOST"),
        os.environ.get("POSTGRES_DB"),
        os.environ.get("POSTGRES_USER"),
        os.environ.get("POSTGRES_PASSWORD"),
    ]):
        print("PostgreSQL configuration is missing. Please set the following environment variables:")
        print("  POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD")
        return
    
    # Create LLM provider
    if os.environ.get("OPENAI_API_KEY"):
        print("Using OpenAI provider")
        llm = OpenAIProvider(
            api_key=os.environ["OPENAI_API_KEY"],
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        )
    else:
        print("Using Ollama provider (local)")
        llm = OllamaProvider(
            model=os.environ.get("OLLAMA_MODEL", "llama3"),
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    
    # Create vector storage
    vector_store = PostgreSQLVectorStorage(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        llm=llm,
    )
    
    # Create a RAG tool
    rag_tool = RAGTool(vector_store=vector_store)
    
    # Create an agent with the RAG tool
    agent = Agent(
        name="knowledge_agent",
        llm=llm,
        tools=[rag_tool],
        system_prompt="You are a knowledge agent that can store and retrieve information. Use the RAG tool to ingest and query documents.",
        description="Knowledge agent that can store and retrieve information",
    )
    
    # Example 1: Ingest text
    print("\n=== Example 1: Ingest Text ===")
    query = """
    Use the RAG tool to ingest the following information into a collection called 'ai_concepts':
    
    Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.
    
    The ideal characteristic of artificial intelligence is its ability to rationalize and take actions that have the best chance of achieving a specific goal. A subset of artificial intelligence is machine learning, which refers to the concept that computer programs can automatically learn from and adapt to new data without being assisted by humans.
    """
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 2: Ingest from URL
    print("\n=== Example 2: Ingest from URL ===")
    query = """
    Use the RAG tool to ingest content from the URL https://en.wikipedia.org/wiki/Machine_learning into a collection called 'ai_concepts'.
    """
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 3: Query the knowledge base
    print("\n=== Example 3: Query the Knowledge Base ===")
    query = """
    Use the RAG tool to query the 'ai_concepts' collection for information about machine learning.
    """
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 4: List collections
    print("\n=== Example 4: List Collections ===")
    query = """
    Use the RAG tool to list all available collections.
    """
    response = await agent.run(query)
    print(f"Response: {response}")
    
    # Example 5: Answering questions using the knowledge base
    print("\n=== Example 5: Answering Questions Using the Knowledge Base ===")
    query = """
    What is the relationship between artificial intelligence and machine learning? Use the RAG tool to find relevant information in the 'ai_concepts' collection.
    """
    response = await agent.run(query)
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
