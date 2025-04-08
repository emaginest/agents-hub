# Cognitive Module for Agents Hub

This module provides a cognitive architecture inspired by human cognition, with metacognitive capabilities and advanced reasoning mechanisms.

## Components

### Metacognition

The metacognition system enables agents to:
- Reflect on their own thinking processes
- Evaluate confidence in their responses
- Identify gaps in knowledge
- Adjust reasoning strategies based on task complexity
- Learn from past experiences

### Reasoning Mechanisms

The reasoning module provides various reasoning strategies:
- **Deductive Reasoning**: Drawing conclusions from general principles
- **Inductive Reasoning**: Forming generalizations from specific observations
- **Abductive Reasoning**: Finding the most likely explanation for observations
- **Analogical Reasoning**: Applying solutions from similar problems
- **Causal Reasoning**: Understanding cause-and-effect relationships

## Usage

### Creating a Cognitive Agent

```python
from agents_hub import CognitiveAgent
from agents_hub.cognitive import CognitiveArchitecture
from agents_hub.llm.providers import ClaudeProvider

# Initialize LLM provider
llm = ClaudeProvider(api_key="your-anthropic-api-key")

# Create cognitive architecture
cognitive_architecture = CognitiveArchitecture(
    metacognition_config={
        "reflection_depth": 2,
        "confidence_threshold": 0.7,
    },
    reasoning_config={
        "enabled_mechanisms": ["deductive", "inductive", "abductive"],
        "default_mechanism": "deductive",
    },
)

# Create cognitive agent
agent = CognitiveAgent(
    name="cognitive_agent",
    llm=llm,
    cognitive_architecture=cognitive_architecture,
    system_prompt="You are a thoughtful assistant with advanced reasoning capabilities.",
    cognitive_config={
        "reasoning_trace_enabled": True,
        "metacognition_enabled": True,
        "learning_enabled": True,
    },
)

# Use the agent with different reasoning mechanisms
response = await agent.run(
    "What might be causing the economic downturn in this region?",
    context={"reasoning_mechanism": "abductive"}
)
```

### Using Metacognition

```python
# Enable self-reflection
response = await agent.run(
    "Is quantum computing likely to replace traditional computing for most applications?",
    context={
        "metacognition": {
            "reflection_enabled": True,
            "confidence_evaluation": True,
            "knowledge_gaps_identification": True,
        }
    }
)

# The response will include:
# - Main answer
# - Confidence assessment
# - Identified knowledge gaps
# - Reflection on reasoning process
```

## Integration with Other Modules

The cognitive module integrates with:
- **Memory System**: To store and retrieve past reasoning traces
- **RAG System**: To enhance reasoning with relevant knowledge
- **Monitoring**: To track reasoning performance and metacognitive insights

## Advanced Features

### Learning from Experience

The cognitive architecture can improve over time by:
- Storing successful reasoning patterns
- Identifying reasoning errors
- Adjusting confidence calibration
- Expanding knowledge representations

### Explainable AI

The module provides transparency through:
- Detailed reasoning traces
- Confidence assessments
- Alternative perspectives consideration
- Explicit metacognitive reflections
