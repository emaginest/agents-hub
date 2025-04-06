"""
Example of a learning cognitive agent in the Agents Hub framework.
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import CognitiveAgent
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.cognitive import CognitiveArchitecture


async def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()

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

    # Create cognitive architecture with enhanced learning
    cognitive_architecture = CognitiveArchitecture(
        learning_config={
            "experience_based_learning": True,
            "strategy_adaptation": True,
            "performance_tracking": True,
            "max_experiences": 10,  # Reduced for faster learning in examples
        }
    )

    # Create cognitive agent with improved learning prompt
    agent = CognitiveAgent(
        name="learning_agent",
        llm=llm,
        cognitive_architecture=cognitive_architecture,
        system_prompt="""You are an intelligent assistant with the ability to learn and improve over time.
        As you encounter more examples, you should:
        1. Identify patterns and relationships in the information
        2. Adapt your reasoning strategies based on feedback
        3. Improve the quality and accuracy of your responses
        4. Demonstrate how your understanding evolves

        Always provide direct, specific answers to questions. When appropriate, reference what you've
        learned from previous interactions to show your learning process.

        IMPORTANT: Do not repeat the question in your answer - focus on providing insightful, accurate responses.""",
        cognitive_config={
            "reasoning_trace_enabled": True,
            "metacognition_enabled": True,
            "learning_enabled": True,
            "reasoning_depth": 3,  # Increased for deeper analysis
            "default_reasoning_mechanism": "inductive",  # Changed to inductive for learning
        },
    )

    # Use a single conversation ID to better demonstrate learning
    conversation_id = "learning_sequence"

    # Example 1: Initial question with a simple topic
    print("\n=== Example 1: Initial Question ===")
    query = "What are the three branches of the US government?"
    response = await agent.run(query, context={"conversation_id": conversation_id})
    print(f"Response: {response}")

    # Example 2: Follow-up that builds on the first question
    print("\n=== Example 2: Follow-up Question ===")
    query = "How do the three branches of government check and balance each other? Be specific about the mechanisms."
    response = await agent.run(query, context={"conversation_id": conversation_id})
    print(f"Response: {response}")

    # Example 3: More complex question requiring synthesis
    print("\n=== Example 3: Complex Synthesis Question ===")
    query = "Can you explain a recent example of checks and balances in action between the branches? Cite a specific case from the last few years."
    response = await agent.run(query, context={"conversation_id": conversation_id})
    print(f"Response: {response}")

    # Example 4: Question with feedback to learn from
    print("\n=== Example 4: Learning from Feedback ===")
    query = "Your previous explanation was good, but you didn't fully address the role of judicial review. Can you explain how judicial review fits into the checks and balances system and provide a specific Supreme Court case as an example?"
    response = await agent.run(query, context={"conversation_id": conversation_id})
    print(f"Response: {response}")

    # Example 5: New but related domain to test transfer learning
    print("\n=== Example 5: Transfer Learning ===")
    query = "How does the separation of powers in the European Union differ from the US system? Focus on 2-3 key differences."
    response = await agent.run(query, context={"conversation_id": conversation_id})
    print(f"Response: {response}")

    # Example 6: Final complex question to demonstrate improvement
    print("\n=== Example 6: Demonstrating Learning and Improvement ===")
    query = "Based on everything we've discussed, what are the strengths and weaknesses of the US checks and balances system compared to other democratic systems? Include insights from our discussion of both US and EU governance."
    response = await agent.run(query, context={"conversation_id": conversation_id})
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
