# Agents Module for Agents Hub

This module provides the core agent functionality for the Agents Hub framework, including the base Agent class and specialized agent implementations.

## Components

### Base Agent

The Agent class provides the foundation for all agents in the framework:
- **LLM Integration**: Connect to language models
- **Memory Management**: Store and retrieve information
- **Tool Usage**: Access and use tools
- **Conversation Handling**: Manage conversations
- **Moderation**: Filter content for safety
- **Monitoring**: Track performance and usage

### Specialized Agents

The specialized directory contains agents optimized for specific tasks:
- **ResearchAgent**: Find and analyze information
- **AnalystAgent**: Evaluate information and draw insights
- **WriterAgent**: Create clear and engaging content
- **CustomerSupportAgent**: Provide helpful support responses
- **TeacherAgent**: Explain concepts and answer questions

### Evolution

The evolution directory contains components for agent self-improvement:
- **LearningAgent**: Improve through experience
- **AdaptiveAgent**: Adjust to user preferences
- **EvolutionaryAgent**: Evolve through feedback

## Usage

### Creating a Basic Agent

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create a basic agent
agent = Agent(
    name="assistant",
    llm=llm,
    system_prompt="You are a helpful assistant."
)

# Use the agent
response = await agent.run("What is the capital of France?")
print(response)
```

### Creating an Agent with Tools

```python
from agents_hub import Agent
from agents_hub.tools.standard import WebSearchTool, CalculatorTool
from agents_hub.llm.providers import ClaudeProvider

# Initialize LLM provider
llm = ClaudeProvider(api_key="your-anthropic-api-key")

# Initialize tools
web_search = WebSearchTool()
calculator = CalculatorTool()

# Create an agent with tools
agent = Agent(
    name="research_assistant",
    llm=llm,
    tools=[web_search, calculator],
    system_prompt="You are a research assistant that can search the web and perform calculations."
)

# Use the agent with tools
response = await agent.run("What is the population of Tokyo and how does it compare to New York City?")
print(response)
```

### Creating an Agent with Memory

```python
from agents_hub import Agent
from agents_hub.memory.backends import PostgreSQLMemory
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Initialize memory backend
memory = PostgreSQLMemory(
    llm=llm,  # For generating embeddings
    host="localhost",
    port=5432,
    database="agents_hub",
    user="postgres",
    password="postgres"
)

# Create an agent with memory
agent = Agent(
    name="memory_agent",
    llm=llm,
    memory=memory,
    system_prompt="You are an assistant that remembers past conversations."
)

# Use the agent with memory
response = await agent.run(
    "What is my name?",
    context={
        "conversation_id": "user123",
        "user_id": "user456"
    }
)
print(response)

# The agent will remember this information
response = await agent.run(
    "My name is Alice.",
    context={
        "conversation_id": "user123",
        "user_id": "user456"
    }
)
print(response)

# The agent can recall the information
response = await agent.run(
    "What is my name?",
    context={
        "conversation_id": "user123",
        "user_id": "user456"
    }
)
print(response)  # Should mention "Alice"
```

## Advanced Features

### Using Specialized Agents

```python
from agents_hub.agents.specialized import ResearchAgent, AnalystAgent, WriterAgent
from agents_hub.llm.providers import OpenAIProvider, ClaudeProvider

# Initialize LLM providers
openai_llm = OpenAIProvider(api_key="your-openai-api-key")
claude_llm = ClaudeProvider(api_key="your-anthropic-api-key")

# Create specialized agents
researcher = ResearchAgent(
    llm=openai_llm,
    research_depth="deep",
    sources_required=True
)

analyst = AnalystAgent(
    llm=claude_llm,
    analysis_framework="SWOT",
    critical_thinking_level="high"
)

writer = WriterAgent(
    llm=claude_llm,
    writing_style="professional",
    tone="informative"
)

# Use specialized agents
research_results = await researcher.research("Impact of artificial intelligence on healthcare")
analysis = await analyst.analyze(research_results)
report = await writer.write_report(analysis)

print(report)
```

### Creating a Learning Agent

```python
from agents_hub.agents.evolution import LearningAgent
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create a learning agent
learning_agent = LearningAgent(
    name="learning_assistant",
    llm=llm,
    learning_rate=0.1,
    feedback_integration="immediate",
    system_prompt="You are a helpful assistant that learns from interactions."
)

# Use the agent
response = await learning_agent.run("What is the best way to learn programming?")
print(response)

# Provide feedback to help the agent learn
await learning_agent.provide_feedback(
    feedback="Your response was helpful but could include more specific resources.",
    score=0.8,
    conversation_id="conv123"
)

# The agent will incorporate the feedback in future responses
response = await learning_agent.run("What is the best way to learn data science?")
print(response)  # Should include more specific resources
```

### Agent Customization

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create a highly customized agent
agent = Agent(
    name="custom_agent",
    llm=llm,
    system_prompt="You are a specialized assistant for financial analysis.",
    tools=[],  # No tools initially
    memory=None,  # No memory initially
    moderation=None,  # No moderation initially
    monitor=None,  # No monitoring initially
    config={
        "temperature": 0.2,  # Lower temperature for more deterministic responses
        "max_tokens": 500,  # Limit response length
        "response_format": "markdown",  # Format responses as markdown
        "thinking_style": "analytical",  # Analytical thinking style
        "persona": "financial_expert",  # Financial expert persona
    }
)

# Add tools dynamically
from agents_hub.tools.standard import CalculatorTool
await agent.add_tool(CalculatorTool())

# Update system prompt
await agent.update_system_prompt(
    "You are a specialized assistant for financial analysis. "
    "You can perform calculations and provide insights on financial data."
)

# Use the agent
response = await agent.run("Analyze the following financial data: Revenue: $1.2M, Expenses: $800K, Growth: 15%")
print(response)
```

## Integration with Other Modules

The agents module integrates with:
- **LLM Module**: For language model capabilities
- **Memory Module**: For storing and retrieving information
- **Tools Module**: For accessing external functionality
- **Moderation Module**: For content filtering
- **Monitoring Module**: For tracking performance
- **Cognitive Module**: For advanced reasoning capabilities
- **Orchestration Module**: For agent collaboration
