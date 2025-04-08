"""
Example of using the PGVector tool to build a RAG (Retrieval-Augmented Generation) system.

This example demonstrates how to:
1. Create a collection
2. Add documents to the collection
3. Search for similar documents
4. Build a simple RAG system using the PGVector tool
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import PGVectorTool, ScraperTool


async def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")
        return
    
    # Create LLM provider
    llm = OpenAIProvider(
        api_key=os.environ["OPENAI_API_KEY"],
        model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
    )
    
    # Create PGVector tool
    pgvector_tool = PGVectorTool(
        llm=llm,
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ.get("POSTGRES_DB", "postgres"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
    )
    
    # Create scraper tool for ingesting web content
    scraper_tool = ScraperTool()
    
    # Create an agent with the PGVector tool
    agent = Agent(
        name="rag_agent",
        llm=llm,
        tools=[pgvector_tool, scraper_tool],
        system_prompt="""You are a knowledge management assistant that helps users build and query a RAG system.
        
        You can:
        1. Create collections to organize documents
        2. Add documents to collections
        3. Search for similar documents
        4. Answer questions based on the retrieved documents
        
        Always use the pgvector tool to store and retrieve information.
        When answering questions, first search for relevant information, then use that information to formulate your response.
        """,
    )
    
    # Example 1: Create a collection
    print("\n=== Example 1: Create a Collection ===")
    query = """
    Create a collection called 'ai_concepts' for storing information about artificial intelligence.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")
    
    response = await agent.run(query)
    
    print("Response:")
    print(response)
    
    # Example 2: Add a document to the collection
    print("\n=== Example 2: Add a Document to the Collection ===")
    query = """
    Add the following document to the 'ai_concepts' collection:
    
    Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.
    
    The ideal characteristic of artificial intelligence is its ability to rationalize and take actions that have the best chance of achieving a specific goal. A subset of artificial intelligence is machine learning, which refers to the concept that computer programs can automatically learn from and adapt to new data without being assisted by humans.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")
    
    response = await agent.run(query)
    
    print("Response:")
    print(response)
    
    # Example 3: Add web content to the collection
    print("\n=== Example 3: Add Web Content to the Collection ===")
    query = """
    Scrape the content from https://en.wikipedia.org/wiki/Machine_learning and add it to the 'ai_concepts' collection.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")
    
    response = await agent.run(query)
    
    print("Response:")
    print(response)
    
    # Example 4: Search the collection
    print("\n=== Example 4: Search the Collection ===")
    query = """
    Search the 'ai_concepts' collection for information about machine learning.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")
    
    response = await agent.run(query)
    
    print("Response:")
    print(response)
    
    # Example 5: Answer a question using RAG
    print("\n=== Example 5: Answer a Question Using RAG ===")
    query = """
    What is the relationship between artificial intelligence and machine learning? Use the information in the 'ai_concepts' collection to answer.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")
    
    response = await agent.run(query)
    
    print("Response:")
    print(response)
    
    # Example 6: List all collections
    print("\n=== Example 6: List All Collections ===")
    query = """
    List all available collections in the database.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")
    
    response = await agent.run(query)
    
    print("Response:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
