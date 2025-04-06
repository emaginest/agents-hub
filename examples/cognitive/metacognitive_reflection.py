"""
Example of metacognitive reflection in the Agents Hub framework.
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

    # Create cognitive architecture with enhanced metacognition
    cognitive_architecture = CognitiveArchitecture(
        metacognition_config={
            "reflection_depth": 3,  # Maximum reflection depth
            "confidence_threshold": 0.6,  # Lower threshold to trigger more metacognition
            "strategy_adaptation": True,
        }
    )

    # Create cognitive agent with improved metacognitive prompt
    agent = CognitiveAgent(
        name="reflective_agent",
        llm=llm,
        cognitive_architecture=cognitive_architecture,
        system_prompt="""You are an intelligent assistant with advanced metacognitive capabilities.
        For each question:
        1. Provide your initial answer based on your knowledge and reasoning
        2. Reflect on your reasoning process and identify potential biases or limitations
        3. Consider alternative perspectives or approaches
        4. Revise your answer if necessary based on your reflection
        5. Explain how your thinking evolved through this process

        Your final answer should incorporate insights from your metacognitive process and
        clearly indicate your level of confidence. When appropriate, acknowledge uncertainty.

        IMPORTANT: Do not repeat the question in your answer - focus on providing thoughtful,
        reflective responses that demonstrate your metacognitive abilities.""",
        cognitive_config={
            "reasoning_trace_enabled": True,
            "metacognition_enabled": True,
            "learning_enabled": False,  # Disable learning to focus on metacognition
            "reasoning_depth": 3,  # Increased for deeper analysis
            "default_reasoning_mechanism": "deductive",
        },
    )

    # Example 1: Simple calculation with high confidence
    print("\n=== Example 1: High Confidence Reasoning ===")
    query = "What is 15% of 80? Show your calculation and reflect on your confidence in the answer."
    response = await agent.run(query)
    print(f"Response: {response}")

    # Example 2: Medium confidence reasoning requiring estimation
    print("\n=== Example 2: Medium Confidence Reasoning ===")
    query = "Approximately how many books are published worldwide each year? Reflect on the reliability of your estimate."
    response = await agent.run(query)
    print(f"Response: {response}")

    # Example 3: Low confidence reasoning with future prediction
    print("\n=== Example 3: Low Confidence Reasoning ===")
    query = "Will artificial general intelligence be developed within the next decade? Consider multiple perspectives and reflect on your uncertainty."
    response = await agent.run(query)
    print(f"Response: {response}")

    # Example 4: Reasoning with incomplete information
    print("\n=== Example 4: Reasoning with Incomplete Information ===")
    query = "Based on limited economic indicators (inflation at 3%, unemployment at 4%, GDP growth at 2%), how is the economy performing? Reflect on what additional information would improve your assessment."
    response = await agent.run(query)
    print(f"Response: {response}")

    # Example 5: Reasoning with conflicting information
    print("\n=== Example 5: Reasoning with Conflicting Information ===")
    query = "Study A suggests coffee is beneficial for health, while Study B suggests it's harmful. What should we conclude about coffee consumption? Reflect on how to reconcile these conflicting findings."
    response = await agent.run(query)
    print(f"Response: {response}")

    # Example 6: Complex problem requiring strategy adaptation
    print("\n=== Example 6: Strategy Adaptation ===")
    query = "How might we solve the housing affordability crisis in major cities? After your initial answer, reflect on what perspectives or solutions you might have overlooked and revise your response."
    response = await agent.run(query)
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
