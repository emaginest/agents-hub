# Orchestration Module for Agents Hub

This module provides orchestration capabilities for the Agents Hub framework, enabling coordination and collaboration between multiple agents to solve complex tasks.

## Components

### Agent Workforce

The AgentWorkforce class manages a team of specialized agents:
- **Task Decomposition**: Breaking down complex tasks into subtasks
- **Agent Selection**: Choosing the right agent for each subtask
- **Task Routing**: Directing tasks to appropriate agents
- **Result Synthesis**: Combining results from multiple agents

### Router

The Router class handles task routing strategies:
- **Round Robin**: Distribute tasks evenly among agents
- **Skill-based**: Route tasks based on agent capabilities
- **Load-balanced**: Distribute tasks based on agent workload
- **Hierarchical**: Use manager agents to delegate to worker agents

### Protocols

The Protocols module defines communication standards:
- **Message Format**: Standardized message structure
- **Task Protocol**: How tasks are represented and tracked
- **Result Protocol**: How results are formatted and returned
- **Error Handling**: How errors are communicated and resolved

## Usage

### Creating an Agent Workforce

```python
from agents_hub import AgentWorkforce, Agent
from agents_hub.llm.providers import OpenAIProvider, ClaudeProvider

# Initialize LLM providers
openai_llm = OpenAIProvider(api_key="your-openai-api-key")
claude_llm = ClaudeProvider(api_key="your-anthropic-api-key")

# Create specialized agents
researcher = Agent(
    name="researcher",
    llm=claude_llm,
    system_prompt="You are a researcher who finds and analyzes information."
)

analyst = Agent(
    name="analyst",
    llm=openai_llm,
    system_prompt="You are an analyst who evaluates information and draws insights."
)

writer = Agent(
    name="writer",
    llm=claude_llm,
    system_prompt="You are a writer who creates clear and engaging content."
)

# Create a workforce with these agents
workforce = AgentWorkforce(
    agents=[researcher, analyst, writer],
    router_config={
        "default_agent": "researcher",
        "routing_strategy": "skill-based"
    }
)
```

### Executing Tasks with the Workforce

```python
# Execute a task with the workforce
result = await workforce.execute(
    "Research the impact of AI on healthcare and prepare a report",
    context={
        "format": "markdown",
        "max_length": 1000,
        "focus_areas": ["diagnosis", "treatment", "patient care"]
    }
)

print(result)
```

### Custom Routing

```python
from agents_hub.orchestration import Router

# Create a custom router
router = Router(
    strategy="custom",
    agent_mapping={
        "research": "researcher",
        "analysis": "analyst",
        "writing": "writer",
        "default": "researcher"
    }
)

# Create a workforce with the custom router
workforce = AgentWorkforce(
    agents=[researcher, analyst, writer],
    router=router
)

# Execute a task with explicit routing
result = await workforce.execute(
    "Analyze the latest research on renewable energy",
    routing_hint="analysis"  # This will route to the analyst agent
)
```

## Advanced Features

### Hierarchical Orchestration

```python
# Create a manager agent
manager = Agent(
    name="manager",
    llm=openai_llm,
    system_prompt="You are a project manager who coordinates tasks and synthesizes results."
)

# Create a hierarchical workforce
hierarchical_workforce = AgentWorkforce(
    agents=[manager, researcher, analyst, writer],
    router_config={
        "default_agent": "manager",
        "routing_strategy": "hierarchical",
        "manager_agent": "manager"
    }
)

# The manager will decompose tasks and coordinate other agents
result = await hierarchical_workforce.execute(
    "Create a comprehensive report on climate change solutions"
)
```

### Parallel Execution

```python
# Execute subtasks in parallel
result = await workforce.execute(
    "Analyze these three companies: Apple, Google, and Microsoft",
    execution_config={
        "parallel": True,
        "max_concurrent_tasks": 3
    }
)
```

### Feedback Loops

```python
# Execute with feedback loops
result = await workforce.execute(
    "Write a technical article about quantum computing",
    execution_config={
        "feedback_loops": True,
        "max_iterations": 3,
        "feedback_agent": "analyst"
    }
)
```

## Integration with Other Modules

The orchestration module integrates with:
- **Cognitive Module**: For metacognitive oversight of agent collaboration
- **Memory Module**: For sharing context between agents
- **Monitoring Module**: For tracking workforce performance
- **Tools Module**: For providing tools to specialized agents

## Specialized Workforces

The framework includes specialized workforce implementations:
- **CodingWorkforce**: For software development tasks
- **ResearchWorkforce**: For research and analysis tasks
- **ContentWorkforce**: For content creation tasks

Example of using a specialized workforce:

```python
from agents_hub.coding import CodingWorkforce

# Create a coding workforce
coding_workforce = CodingWorkforce(
    llm_mapping={
        "project_manager": openai_llm,
        "backend_developer": claude_llm,
        "frontend_developer": claude_llm,
        "devops_engineer": openai_llm
    },
    project_name="TaskManager",
    project_description="A task management application with a FastAPI backend and a React frontend."
)

# Develop a complete software project
project_dir = await coding_workforce.develop_project()
```
