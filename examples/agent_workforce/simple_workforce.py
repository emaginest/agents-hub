"""
Simple example of using the Agents Hub framework to create a workforce of agents.
"""

import os
import asyncio
from dotenv import load_dotenv

from agents_hub import Agent, AgentWorkforce
from agents_hub.llm.providers import OpenAIProvider, OllamaProvider
from agents_hub.tools.standard import CalculatorTool


async def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Create LLM providers
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
    
    # Create a calculator tool
    calculator_tool = CalculatorTool()
    
    # Create specialized agents
    researcher = Agent(
        name="researcher",
        llm=llm,
        tools=[calculator_tool],
        system_prompt="You are a helpful research assistant. Your job is to provide accurate, well-researched information on any topic. Always cite your sources when possible.",
        description="Research assistant that provides accurate information on any topic",
    )
    
    writer = Agent(
        name="writer",
        llm=llm,
        system_prompt="You are a skilled writer and editor. Your job is to help create, refine, and improve written content. You can help with drafting, editing, proofreading, and providing feedback on writing style and structure.",
        description="Writer and editor that helps create and improve written content",
    )
    
    coder = Agent(
        name="coder",
        llm=llm,
        system_prompt="You are an expert programmer. Your job is to write clean, efficient, and well-documented code. You can help with coding tasks, debugging, code reviews, and explaining technical concepts.",
        description="Programmer that writes and explains code",
    )
    
    # Create an orchestrator agent
    orchestrator = Agent(
        name="orchestrator",
        llm=llm,
        system_prompt="You are a task orchestrator. Your job is to break down complex tasks into smaller subtasks and assign them to the most appropriate specialized agents. You then synthesize their outputs into a cohesive final result.",
        description="Task orchestrator that coordinates other agents",
    )
    
    # Create a workforce with these agents
    workforce = AgentWorkforce(
        agents=[researcher, writer, coder],
        orchestrator_agent=orchestrator,
    )
    
    # Execute a task with the workforce
    task = "Research the latest advancements in quantum computing and write a 3-paragraph summary for a technical audience. Include a simple Python code example that demonstrates quantum superposition conceptually."
    
    print(f"\nExecuting task: {task}\n")
    result = await workforce.execute(task)
    
    print("\n=== Result ===\n")
    print(result["result"])
    
    print("\n=== Subtasks ===\n")
    for subtask in result.get("subtasks", []):
        print(f"Agent: {subtask['agent']}")
        print(f"Task: {subtask['description']}")
        print("---")


if __name__ == "__main__":
    asyncio.run(main())
