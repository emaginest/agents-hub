"""
Advanced Cognitive Agent Example

This example demonstrates the full potential of cognitive agents with:
1. Complex reasoning across multiple domains
2. Metacognitive reflection and self-correction
3. Learning and adaptation from experience
4. Integration of multiple reasoning mechanisms
5. Problem-solving with incomplete information
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import CognitiveAgent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.cognitive import CognitiveArchitecture


async def main():
    """Run the advanced cognitive agent example."""
    # Load environment variables from .env file
    load_dotenv()

    # Check if API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        print("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")
        return

    # Create LLM provider
    llm = OpenAIProvider(
        api_key=os.environ["OPENAI_API_KEY"],
        model=os.environ.get("OPENAI_MODEL", "gpt-4o"),
    )
    print(f"Using OpenAI provider with model: {os.environ.get('OPENAI_MODEL', 'gpt-4o')}")

    # Create cognitive architecture with enhanced capabilities
    cognitive_architecture = CognitiveArchitecture(
        # Enhanced metacognition configuration
        metacognition_config={
            "reflection_depth": 3,
            "confidence_threshold": 0.6,
            "strategy_adaptation": True,
        },
        # Enhanced learning configuration
        learning_config={
            "experience_based_learning": True,
            "strategy_adaptation": True,
            "performance_tracking": True,
            "max_experiences": 10,
        },
    )

    # Create advanced cognitive agent
    agent = CognitiveAgent(
        name="advanced_cognitive_agent",
        llm=llm,
        cognitive_architecture=cognitive_architecture,
        system_prompt="""You are an advanced cognitive agent with sophisticated reasoning, learning, and metacognitive capabilities.

        Your abilities include:
        1. Using multiple reasoning mechanisms (deductive, inductive, abductive, analogical, causal)
        2. Learning from experience and adapting your strategies
        3. Reflecting on your own reasoning process and correcting errors
        4. Handling uncertainty and incomplete information
        5. Solving complex problems across multiple domains

        When responding:
        - Provide clear, direct answers that address the core question
        - Explain your reasoning process when appropriate
        - Acknowledge uncertainty when present
        - Consider multiple perspectives and approaches
        - Draw on relevant knowledge across domains
        """,
        cognitive_config={
            "reasoning_trace_enabled": True,
            "metacognition_enabled": True,
            "learning_enabled": True,
            "reasoning_depth": 3,
            "default_reasoning_mechanism": "deductive",
        },
    )

    # Create a conversation ID to track learning across examples
    conversation_id = "advanced_cognitive_example"

    # Example 1: Complex ethical dilemma requiring multiple reasoning mechanisms
    print("\n=== Example 1: Complex Ethical Dilemma ===")
    query = """
    Consider the trolley problem: A runaway trolley is headed for five people who will be killed unless the trolley is diverted to a different track where it will kill one person instead.

    Now consider these variations:
    1. The one person is a renowned surgeon who would save thousands of lives
    2. The five people are elderly while the one person is a child
    3. You have to physically push someone onto the tracks to stop the trolley

    What is the ethically correct action in each scenario? Explain your reasoning, considering utilitarian, deontological, and virtue ethics perspectives.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")

    response = await agent.run(query, context={"conversation_id": conversation_id})

    print("Response:")
    print(response)

    # Example 2: Scientific reasoning with incomplete information
    print("\n=== Example 2: Scientific Reasoning with Incomplete Information ===")
    query = """
    Scientists have observed the following phenomena on an exoplanet:
    1. The atmosphere contains methane and oxygen
    2. There are seasonal changes in surface coloration
    3. There are regular radio emissions that follow a pattern

    What hypotheses might explain these observations? Evaluate each hypothesis based on the available evidence, identify what additional information would be most valuable to collect, and explain how you would test these hypotheses.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")

    response = await agent.run(query, context={"conversation_id": conversation_id})

    print("Response:")
    print(response)

    # Example 3: Strategic problem-solving with constraints
    print("\n=== Example 3: Strategic Problem-Solving with Constraints ===")
    query = """
    You are advising a small country facing these challenges:
    1. Limited fresh water resources that are declining by 5% annually
    2. 70% dependence on imported food
    3. 85% dependence on fossil fuel energy
    4. Rising sea levels threatening 30% of habitable land
    5. Limited financial resources ($2 billion annual budget)

    Develop a 10-year strategic plan that addresses these interconnected challenges. Prioritize actions, consider trade-offs, and explain the reasoning behind your strategy.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")

    response = await agent.run(query, context={"conversation_id": conversation_id})

    print("Response:")
    print(response)

    # Example 4: Learning from feedback and adapting
    print("\n=== Example 4: Learning from Feedback and Adapting ===")
    query = """
    Your strategic plan was well-reasoned but overlooked two critical factors:
    1. The country has a rapidly aging population (median age increasing from 35 to 45 over the next decade)
    2. The country has strong research universities with expertise in biotechnology and renewable energy

    How does this additional information change your strategic recommendations? Revise your plan accordingly and explain how these factors influence your thinking.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")

    response = await agent.run(query, context={"conversation_id": conversation_id})

    print("Response:")
    print(response)

    # Example 5: Cross-domain integration and creative problem-solving
    print("\n=== Example 5: Cross-Domain Integration and Creative Problem-Solving ===")
    query = """
    Consider how principles from these different domains might help solve the challenge of sustainable urban transportation:
    1. Biological systems and how organisms efficiently move and use energy
    2. Information technology and network optimization
    3. Behavioral economics and human decision-making
    4. Materials science and emerging technologies

    Develop an innovative transportation solution that integrates insights from at least three of these domains. Explain the underlying principles and how they work together in your solution.
    """
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")

    response = await agent.run(query, context={"conversation_id": conversation_id})

    print("Response:")
    print(response)

    # End of examples
    print("\n=== End of Advanced Cognitive Agent Examples ===")
    print("\nThe advanced cognitive agent has demonstrated complex reasoning across multiple domains.")
    print("For metacognitive reflection capabilities, see the metacognitive_analysis.py example.")


if __name__ == "__main__":
    asyncio.run(main())
