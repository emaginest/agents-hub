# Cognitive Architecture in Agents Hub

The Agents Hub framework includes a cognitive architecture inspired by human cognition, providing agents with advanced reasoning capabilities, metacognitive reflection, and learning from experience.

## Overview

The cognitive architecture in Agents Hub is designed to:

1. **Process Information**: Analyze and extract features from input
2. **Reason Effectively**: Apply different reasoning mechanisms based on the task
3. **Reflect on Reasoning**: Evaluate reasoning quality and confidence
4. **Learn from Experience**: Adapt strategies based on performance

The architecture consists of multiple layers that work together to provide human-like cognitive capabilities:

- **Perception Layer**: Processes input and extracts features
- **Working Memory**: Stores active information during processing
- **Reasoning Layer**: Applies different reasoning mechanisms
- **Metacognitive Layer**: Reflects on reasoning quality and confidence
- **Learning Layer**: Adapts strategies based on experience

## Cognitive Agent

The `CognitiveAgent` class extends the base `Agent` class with cognitive architecture capabilities:

```python
from agents_hub import CognitiveAgent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.cognitive import CognitiveArchitecture

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create cognitive architecture
cognitive_architecture = CognitiveArchitecture()

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
        "reasoning_depth": 2,
        "default_reasoning_mechanism": "deductive",
    },
)

# Use the agent
response = await agent.run(
    "If all birds can fly, and penguins are birds, can penguins fly?",
    context={"reasoning_mechanism": "deductive"},
)
```

## Cognitive Architecture Components

### Perception

The perception layer processes input text and extracts features:

- **Feature Extraction**: Identifies entities, keywords, and patterns
- **Context Recognition**: Recognizes context from input and history
- **Attention Mechanism**: Focuses on relevant parts of the input

```python
from agents_hub.cognitive import Perception

# Create perception layer
perception = Perception(
    feature_extraction=True,
    context_recognition=True,
    attention_mechanism=True,
    max_features=10,
)

# Process input
result = await perception.process(
    input_text="If all birds can fly, and penguins are birds, can penguins fly?",
    context={},
)
```

### Working Memory

The working memory system stores active information during processing:

- **Limited Capacity**: Mimics human working memory limitations
- **Decay**: Information decays over time
- **Chunking**: Groups related items for efficient storage
- **Prioritization**: Prioritizes recent and relevant information

```python
from agents_hub.cognitive import WorkingMemory

# Create working memory
memory = WorkingMemory(
    capacity=7,  # Miller's Law: 7 ± 2 items
    decay_rate=0.1,
    chunking_enabled=True,
    prioritization_enabled=True,
)

# Update memory
memory_state = await memory.update(perception_result, context)
```

### Reasoning

The reasoning layer applies different reasoning mechanisms based on the task:

- **Deductive Reasoning**: Drawing logical conclusions from premises
- **Inductive Reasoning**: Drawing general conclusions from specific observations
- **Abductive Reasoning**: Forming the most likely explanation for observations
- **Analogical Reasoning**: Drawing parallels between different situations or domains
- **Causal Reasoning**: Identifying cause-effect relationships

```python
from agents_hub.cognitive.reasoning import ReasoningManager

# Create reasoning manager
reasoning = ReasoningManager(
    enabled_mechanisms=["deductive", "inductive", "abductive", "analogical", "causal"],
    default_mechanism="deductive",
)

# Apply reasoning
reasoning_result = await reasoning.reason(memory_state, context)
```

### Metacognition

The metacognitive layer reflects on reasoning quality and confidence:

- **Self-Reflection**: Evaluates reasoning quality
- **Confidence Estimation**: Estimates confidence in reasoning
- **Error Detection**: Detects and corrects errors
- **Strategy Selection**: Selects appropriate reasoning strategies

```python
from agents_hub.cognitive import Metacognition

# Create metacognition layer
metacognition = Metacognition(
    reflection_depth=2,
    confidence_threshold=0.7,
    strategy_adaptation=True,
)

# Reflect on reasoning
metacognition_result = await metacognition.reflect(reasoning_result, context)
```

### Learning

The learning layer adapts strategies based on experience:

- **Experience-Based Learning**: Learns from past experiences
- **Strategy Adaptation**: Adapts reasoning strategies
- **Performance Tracking**: Tracks reasoning performance
- **Insight Generation**: Generates insights from experience

```python
from agents_hub.cognitive import Learning

# Create learning layer
learning = Learning(
    experience_based_learning=True,
    strategy_adaptation=True,
    performance_tracking=True,
    max_experiences=100,
)

# Update learning
learning_result = await learning.update(metacognition_result, context)
```

## Reasoning Mechanisms

### Deductive Reasoning

Deductive reasoning involves drawing logical conclusions from premises:

```python
# Example of deductive reasoning
query = "If all birds can fly, and penguins are birds, can penguins fly?"
response = await agent.run(query, context={"reasoning_mechanism": "deductive"})
```

### Inductive Reasoning

Inductive reasoning involves drawing general conclusions from specific observations:

```python
# Example of inductive reasoning
query = "Every time I water my plant, it grows better. What does this suggest about plants in general?"
response = await agent.run(query, context={"reasoning_mechanism": "inductive"})
```

### Abductive Reasoning

Abductive reasoning involves forming the most likely explanation for observations:

```python
# Example of abductive reasoning
query = "The sidewalk is wet this morning. What might have caused this?"
response = await agent.run(query, context={"reasoning_mechanism": "abductive"})
```

### Analogical Reasoning

Analogical reasoning involves drawing parallels between different situations or domains:

```python
# Example of analogical reasoning
query = "How is the structure of an atom similar to our solar system?"
response = await agent.run(query, context={"reasoning_mechanism": "analogical"})
```

### Causal Reasoning

Causal reasoning involves identifying cause-effect relationships:

```python
# Example of causal reasoning
query = "What are the potential effects of rising global temperatures on polar ice caps?"
response = await agent.run(query, context={"reasoning_mechanism": "causal"})
```

## Metacognitive Reflection

The cognitive architecture includes metacognitive reflection capabilities:

```python
# Example of metacognitive reflection
query = "What are the main causes of climate change?"
response = await agent.run(query, context={"reflection_depth": 3})
```

The reflection depth can be configured to control the level of self-reflection:

- **Level 1**: Basic reflection on reasoning quality
- **Level 2**: Deeper reflection on reasoning process
- **Level 3**: Meta-reflection on thinking and biases

## Learning from Experience

The cognitive architecture can learn from experience and adapt strategies:

```python
# Example of learning from experience
query1 = "What are the key factors that contribute to economic growth?"
response1 = await agent.run(query1, context={"conversation_id": "economics"})

# Follow-up question (learning from previous interaction)
query2 = "How do these factors interact with each other?"
response2 = await agent.run(query2, context={"conversation_id": "economics"})
```

## Cognitive Agent Configuration

The `CognitiveAgent` class supports the following configuration options:

```python
cognitive_config = {
    # Whether to include reasoning traces in responses
    "reasoning_trace_enabled": True,
    
    # Whether to enable metacognitive reflection
    "metacognition_enabled": True,
    
    # Whether to enable learning from experience
    "learning_enabled": True,
    
    # Depth of reasoning (1-3)
    "reasoning_depth": 2,
    
    # Default reasoning mechanism
    "default_reasoning_mechanism": "deductive",
}
```

## Context Parameters

When using a cognitive agent, you can provide the following context parameters:

```python
context = {
    # Specify the reasoning mechanism to use
    "reasoning_mechanism": "deductive",
    
    # Use multiple reasoning mechanisms
    "use_multiple_mechanisms": True,
    
    # Specify the reflection depth
    "reflection_depth": 2,
    
    # Conversation ID for learning from experience
    "conversation_id": "unique_id",
}
```

## Best Practices

1. **Choose the Right Reasoning Mechanism**: Select the appropriate reasoning mechanism for the task:
   - Use deductive reasoning for logical problems
   - Use inductive reasoning for pattern recognition
   - Use abductive reasoning for explanation generation
   - Use analogical reasoning for comparison tasks
   - Use causal reasoning for cause-effect analysis

2. **Enable Metacognitive Reflection**: Enable metacognitive reflection for complex problems to improve reasoning quality.

3. **Use Consistent Conversation IDs**: Use consistent conversation IDs to enable learning from experience.

4. **Include Reasoning Traces**: Include reasoning traces in responses to provide transparency.

5. **Combine with Other Capabilities**: Combine cognitive capabilities with other Agents Hub features like tools, memory, and monitoring.

## Examples

### Basic Cognitive Agent

```python
from agents_hub import CognitiveAgent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.cognitive import CognitiveArchitecture

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create cognitive architecture
cognitive_architecture = CognitiveArchitecture()

# Create cognitive agent
agent = CognitiveAgent(
    name="cognitive_agent",
    llm=llm,
    cognitive_architecture=cognitive_architecture,
    system_prompt="You are a thoughtful assistant with advanced reasoning capabilities.",
)

# Use the agent
response = await agent.run("If all birds can fly, and penguins are birds, can penguins fly?")
```

### Metacognitive Reflection

```python
from agents_hub import CognitiveAgent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.cognitive import CognitiveArchitecture, Metacognition

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create cognitive architecture with enhanced metacognition
cognitive_architecture = CognitiveArchitecture(
    metacognition_config={
        "reflection_depth": 3,
        "confidence_threshold": 0.7,
        "strategy_adaptation": True,
    }
)

# Create cognitive agent
agent = CognitiveAgent(
    name="reflective_agent",
    llm=llm,
    cognitive_architecture=cognitive_architecture,
    system_prompt="You are a thoughtful assistant with advanced metacognitive capabilities.",
)

# Use the agent
response = await agent.run("What are the main causes of climate change?")
```

### Learning Agent

```python
from agents_hub import CognitiveAgent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.cognitive import CognitiveArchitecture, Learning

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create cognitive architecture with enhanced learning
cognitive_architecture = CognitiveArchitecture(
    learning_config={
        "experience_based_learning": True,
        "strategy_adaptation": True,
        "performance_tracking": True,
        "max_experiences": 100,
    }
)

# Create cognitive agent
agent = CognitiveAgent(
    name="learning_agent",
    llm=llm,
    cognitive_architecture=cognitive_architecture,
    system_prompt="You are a thoughtful assistant with advanced learning capabilities.",
)

# Use the agent
response1 = await agent.run(
    "What are the key factors that contribute to economic growth?",
    context={"conversation_id": "economics"},
)

response2 = await agent.run(
    "How do these factors interact with each other?",
    context={"conversation_id": "economics"},
)
```

## Troubleshooting

### Common Issues

1. **Low Confidence**: If the agent has low confidence in its reasoning, try:
   - Using a different reasoning mechanism
   - Providing more context
   - Enabling multiple reasoning mechanisms

2. **Incorrect Reasoning**: If the agent's reasoning is incorrect, try:
   - Specifying the reasoning mechanism explicitly
   - Increasing the reflection depth
   - Providing more specific instructions

3. **Slow Performance**: If the agent is slow, try:
   - Reducing the reflection depth
   - Disabling multiple reasoning mechanisms
   - Simplifying the query

### Debugging

To debug cognitive processing, you can examine the reasoning trace:

```python
# Enable reasoning trace
response = await agent.run(
    "What is the best approach to solve this problem?",
    context={"reasoning_trace_enabled": True},
)
```

## Resources

- [Cognitive Science](https://plato.stanford.edu/entries/cognitive-science/)
- [Metacognition](https://en.wikipedia.org/wiki/Metacognition)
- [Reasoning Types](https://en.wikipedia.org/wiki/Reasoning)
- [Working Memory](https://en.wikipedia.org/wiki/Working_memory)
