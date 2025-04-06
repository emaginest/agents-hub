"""
Example of using a cognitive agent in the Agents Hub framework.
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

    # Create cognitive architecture with default settings
    cognitive_architecture = CognitiveArchitecture()

    # Create cognitive agent with improved system prompt
    agent = CognitiveAgent(
        name="cognitive_agent",
        llm=llm,
        cognitive_architecture=cognitive_architecture,
        system_prompt="""You are an intelligent assistant with advanced reasoning capabilities.
        When asked a question, you should:
        1. Analyze the question carefully
        2. Apply the appropriate reasoning mechanism
        3. Provide a clear, direct answer to the question
        4. Explain your reasoning process
        Do not repeat the question in your answer - focus on providing the answer itself.""",
        cognitive_config={
            "reasoning_trace_enabled": True,
            "metacognition_enabled": True,
            "learning_enabled": False,  # Disable learning for basic examples
            "reasoning_depth": 3,  # Increase reasoning depth for better analysis
            "default_reasoning_mechanism": "deductive",
        },
    )

    # Example 1: Deductive reasoning with explicit instruction
    print("\n=== Example 1: Deductive Reasoning ===")
    query = "If all birds can fly, and penguins are birds, can penguins fly? Provide a yes or no answer and explain your reasoning."
    response = await agent.run(query, context={"reasoning_mechanism": "deductive"})
    print(f"Response: {response}")

    # Example 2: Inductive reasoning with clearer example
    print("\n=== Example 2: Inductive Reasoning ===")
    query = "The sun has risen in the east every day for thousands of years. Where will the sun rise tomorrow? Explain your reasoning using inductive logic."
    response = await agent.run(query, context={"reasoning_mechanism": "inductive"})
    print(f"Response: {response}")

    # Example 3: Abductive reasoning with medical example
    print("\n=== Example 3: Abductive Reasoning ===")
    query = "A patient has a fever, cough, and fatigue. What is the most likely explanation for these symptoms? Provide a specific diagnosis and explain your abductive reasoning."
    response = await agent.run(query, context={"reasoning_mechanism": "abductive"})
    print(f"Response: {response}")

    # Example 4: Analogical reasoning with explicit instruction
    print("\n=== Example 4: Analogical Reasoning ===")
    query = "How is the structure of an atom similar to our solar system? Explain the analogy in detail, including both similarities and limitations of this comparison."
    response = await agent.run(query, context={"reasoning_mechanism": "analogical"})
    print(f"Response: {response}")

    # Example 5: Causal reasoning with specific instruction
    print("\n=== Example 5: Causal Reasoning ===")
    query = "What causes the tides on Earth? Explain the causal relationship between the moon, sun, and Earth's tides, identifying primary and secondary causes."
    response = await agent.run(query, context={"reasoning_mechanism": "causal"})
    print(f"Response: {response}")

    # Example 6: Multiple reasoning mechanisms with complex question
    print("\n=== Example 6: Multiple Reasoning Mechanisms ===")
    query = "Should self-driving cars be programmed to prioritize passenger safety or pedestrian safety in unavoidable accident scenarios? Analyze this ethical dilemma using multiple reasoning approaches."
    response = await agent.run(query, context={"use_multiple_mechanisms": True})
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
