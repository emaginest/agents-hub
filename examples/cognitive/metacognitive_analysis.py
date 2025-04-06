"""
Metacognitive Analysis Example

This example demonstrates a cognitive agent's ability to analyze its own reasoning
processes and provide metacognitive insights about its problem-solving approaches.
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import CognitiveAgent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.cognitive import CognitiveArchitecture


async def main():
    """Run the metacognitive analysis example."""
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
    
    # Create cognitive architecture
    cognitive_architecture = CognitiveArchitecture(
        metacognition_config={
            "reflection_depth": 3,
            "confidence_threshold": 0.6,
            "strategy_adaptation": True,
        }
    )
    
    # Create metacognitive agent
    agent = CognitiveAgent(
        name="metacognitive_agent",
        llm=llm,
        cognitive_architecture=cognitive_architecture,
        system_prompt="""You are an advanced cognitive agent with sophisticated metacognitive capabilities.
        
        Your primary task is to analyze your own reasoning processes and provide insights about your problem-solving approaches.
        
        When reflecting on your reasoning:
        1. Identify patterns in how you approach different types of problems
        2. Evaluate your strengths and limitations in reasoning
        3. Consider how your thinking evolves through a conversation
        4. Suggest strategies for improving your reasoning
        
        Be specific and provide examples to illustrate your metacognitive insights.
        """,
        cognitive_config={
            "reasoning_trace_enabled": True,
            "metacognition_enabled": True,
            "learning_enabled": True,
            "reasoning_depth": 3,
            "default_reasoning_mechanism": "deductive",
        },
    )
    
    # Example: Metacognitive analysis of problem-solving approaches
    print("\n=== Metacognitive Analysis of Problem-Solving Approaches ===")
    query = """
    Analyze how you would approach these different types of problems:
    
    1. Ethical Dilemma: The trolley problem - should you divert a trolley to save five people at the cost of one person's life?
    
    2. Scientific Investigation: Scientists discover an exoplanet with methane, oxygen, and regular radio emissions. What hypotheses might explain these observations?
    
    3. Strategic Planning: A small country faces declining water resources, food import dependence, and rising sea levels. How would you develop a strategic plan?
    
    4. Creative Problem-Solving: Design an innovative transportation system that integrates principles from biology, information technology, and behavioral economics.
    
    For each problem:
    - Describe your reasoning approach
    - Identify the reasoning mechanisms you would use
    - Explain how you would handle uncertainty
    - Reflect on potential biases in your reasoning
    
    Then provide a metacognitive analysis of your overall problem-solving patterns, strengths, limitations, and strategies for improvement.
    """
    
    print("Query:")
    print(query)
    print("\n" + "-"*80 + "\n")
    
    response = await agent.run(query)
    
    print("Response:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
