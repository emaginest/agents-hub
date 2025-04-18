"""
Example of building a document Q&A system using the PGVector tool.

This example demonstrates how to:
1. Create a collection in PostgreSQL
2. Add a document with automatic chunking
3. Ask questions about the document using vector similarity search
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.vector_stores import PGVector
from agents_hub.tools.standard import ScraperTool


# Sample document about artificial intelligence
SAMPLE_DOCUMENT = """
# Artificial Intelligence: An Overview

Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.

## Types of Artificial Intelligence

### Narrow AI (Weak AI)
Narrow AI is designed to perform a narrow task (e.g., facial recognition, speech recognition, driving a car, or searching the internet). Most of the AI that surrounds us today is narrow AI.

### General AI (Strong AI)
General AI would have all of the capabilities of human intelligence, including the ability to learn, reason, solve problems, perceive, and understand language. This type of AI does not yet exist but is the primary goal of many AI researchers.

## Key AI Technologies

### Machine Learning
Machine learning is a subset of AI that provides systems the ability to automatically learn and improve from experience without being explicitly programmed. It focuses on the development of computer programs that can access data and use it to learn for themselves.

### Deep Learning
Deep learning is a subset of machine learning that uses neural networks with many layers (hence "deep") to analyze various factors of data. It is particularly useful for processing unstructured data such as images, text, and audio.

### Natural Language Processing (NLP)
NLP is a field of AI that gives machines the ability to read, understand, and derive meaning from human languages. Applications include chatbots, translation services, and sentiment analysis.

### Computer Vision
Computer vision is a field of AI that enables computers to derive meaningful information from digital images, videos, and other visual inputs. Applications include facial recognition, autonomous vehicles, and medical image analysis.

## Ethical Considerations

As AI becomes more advanced, ethical considerations become increasingly important:

1. **Privacy**: AI systems often require large amounts of data, raising concerns about privacy and data protection.
2. **Bias**: AI systems can perpetuate and amplify existing biases in their training data.
3. **Accountability**: Who is responsible when an AI system makes a mistake?
4. **Job Displacement**: As AI automates more tasks, there are concerns about job displacement.
5. **Autonomy**: As AI systems become more autonomous, questions arise about human control and oversight.

## Future of AI

The future of AI is likely to involve continued progress in areas such as:

- More sophisticated natural language understanding and generation
- Improved computer vision capabilities
- More advanced robotics
- Greater integration of AI into everyday devices and services
- Progress toward general AI, though this remains a long-term goal

As AI continues to evolve, it will be important to ensure that it is developed and used in ways that benefit humanity while minimizing potential risks.
"""


async def main():
    """Run the document Q&A example."""
    # Load environment variables from .env file
    load_dotenv()

    # Check if API key is available
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")
        return

    # Initialize LLM provider
    llm = OpenAIProvider(
        api_key=api_key,
        model=os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
    )

    # Initialize PGVector tool
    pgvector_tool = PGVector(
        llm=llm,
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        database=os.environ.get("POSTGRES_DB", "agents_hub"),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
    )

    # Initialize scraper tool (optional, for web content)
    scraper_tool = ScraperTool()

    # Create an agent with the PGVector and scraper tools
    agent = Agent(
        name="document_qa_agent",
        llm=llm,
        tools=[pgvector_tool, scraper_tool],
        system_prompt="""You are a document Q&A assistant that can answer questions about stored documents.
        
You have access to a vector database through the pgvector tool. Use this tool to:
1. Create collections to organize documents
2. Store documents in collections with automatic chunking
3. Search for relevant document chunks when answering questions
4. Provide accurate answers based on the retrieved information

When answering questions:
1. First search for relevant information using the pgvector tool
2. Use the retrieved information to formulate your answer
3. Cite the specific parts of the document you used
4. If the information is not in the document, say so

You can also use the scraper tool to fetch content from websites and add it to your knowledge base."""
    )

    print("📚 Document Q&A Example")
    print("=======================")

    # Step 1: Create a collection
    print("\n📁 Creating a collection...")
    collection_name = "ai_document"
    create_result = await agent.run(
        f"Create a new collection called '{collection_name}' for storing an AI document."
    )
    print(f"Agent response: {create_result}")

    # Step 2: Add the document with automatic chunking
    print("\n📝 Adding document with automatic chunking...")
    add_result = await agent.run(
        f"""Add this document to the '{collection_name}' collection with automatic chunking:
        
{SAMPLE_DOCUMENT}"""
    )
    print(f"Agent response: {add_result}")

    # Step 3: Ask questions about the document
    questions = [
        "What is the difference between narrow AI and general AI?",
        "What are the main ethical considerations mentioned in the document?",
        "What is machine learning and how does it relate to deep learning?",
        "What does the document say about the future of AI?",
        "What is not mentioned in the document about AI?"
    ]

    for i, question in enumerate(questions):
        print(f"\n❓ Question {i+1}: {question}")
        answer_result = await agent.run(
            f"Answer this question using information from the '{collection_name}' collection: \"{question}\""
        )
        print(f"Agent response: {answer_result}")

    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(main())
