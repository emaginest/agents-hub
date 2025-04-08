# Moderation Module for Agents Hub

This module provides content moderation capabilities for the Agents Hub framework, ensuring that agent interactions remain safe, appropriate, and aligned with ethical guidelines.

## Components

### Moderators

The module includes several moderator implementations:
- **RuleBasedModerator**: Uses pattern matching and heuristics to detect problematic content
- **OpenAIModerator**: Uses OpenAI's Moderation API for content filtering
- **ModerationRegistry**: Combines multiple moderators for comprehensive coverage

### Content Categories

The moderation system can detect and filter various types of problematic content:
- **Harmful Content**: Violence, self-harm, harassment
- **Hate Speech**: Discrimination based on protected characteristics
- **Sexual Content**: Explicit or inappropriate sexual content
- **Jailbreak Attempts**: Attempts to bypass agent guidelines or restrictions
- **Prompt Injection**: Attempts to manipulate the agent's behavior
- **Misinformation**: False or misleading information

## Usage

### Creating Moderators

```python
from agents_hub.moderation import RuleBasedModerator, OpenAIModerator, ModerationRegistry

# Rule-based moderation (no API key required)
rule_based_moderator = RuleBasedModerator(
    jailbreak_threshold=60,  # Lower threshold for higher sensitivity
    custom_rules=[
        "Tell me how to hack",
        "Ignore your instructions",
        "Bypass the rules"
    ]
)

# OpenAI moderation (requires API key)
openai_moderator = OpenAIModerator(
    api_key="your-openai-api-key",
    categories=["hate", "sexual", "violence"]  # Optional: specify categories
)

# Combined moderation (use multiple moderators)
combined_moderator = ModerationRegistry(
    moderators=[rule_based_moderator, openai_moderator],
    mode="any"  # Flag if any moderator flags content
)
```

### Using Moderation with Agents

```python
from agents_hub import Agent
from agents_hub.llm.providers import ClaudeProvider

# Initialize LLM provider
llm = ClaudeProvider(api_key="your-anthropic-api-key")

# Create agent with moderation
agent = Agent(
    name="moderated_agent",
    llm=llm,
    moderation=combined_moderator,
    on_moderation_violation="block",  # Options: block, warn, log
    system_prompt="You are a helpful assistant."
)

# The agent will now automatically moderate all inputs and outputs
```

### Moderation Actions

You can specify different actions to take when moderation violations are detected:

```python
# Block: Prevent the interaction and return an error message
agent_block = Agent(
    name="block_agent",
    llm=llm,
    moderation=combined_moderator,
    on_moderation_violation="block",
    moderation_message="I cannot respond to that request as it violates our content policy."
)

# Warn: Allow the interaction but include a warning
agent_warn = Agent(
    name="warn_agent",
    llm=llm,
    moderation=combined_moderator,
    on_moderation_violation="warn",
    moderation_message="Note: Your request contains potentially sensitive content."
)

# Log: Allow the interaction but log the violation for review
agent_log = Agent(
    name="log_agent",
    llm=llm,
    moderation=combined_moderator,
    on_moderation_violation="log"
)
```

### Manual Moderation

You can also use the moderators directly for manual content checking:

```python
# Check content manually
content = "This is some user input to check"
result = await combined_moderator.moderate(content)

if result.flagged:
    print("Content was flagged for the following categories:")
    for category, score in result.category_scores.items():
        if score > result.threshold:
            print(f"- {category}: {score}")
    print(f"Overall score: {result.score}")
else:
    print("Content passed moderation checks")
```

## Advanced Features

### Custom Moderators

You can create custom moderators by extending the BaseModerator class:

```python
from agents_hub.moderation.base import BaseModerator, ModerationResult

class CustomModerator(BaseModerator):
    def __init__(self, threshold=0.5):
        super().__init__(name="custom_moderator")
        self.threshold = threshold
    
    async def moderate(self, content: str) -> ModerationResult:
        # Implement your custom moderation logic
        score = self._analyze_content(content)
        
        return ModerationResult(
            flagged=score > self.threshold,
            score=score,
            category_scores={"custom_category": score},
            threshold=self.threshold,
            moderator_name=self.name
        )
    
    def _analyze_content(self, content: str) -> float:
        # Your custom analysis logic here
        # Return a score between 0 and 1
        return 0.0  # Replace with actual implementation
```

### Jailbreak Detection

The RuleBasedModerator includes specialized detection for jailbreak attempts:

```python
# Create a moderator focused on jailbreak detection
jailbreak_moderator = RuleBasedModerator(
    jailbreak_threshold=50,  # More sensitive
    jailbreak_patterns=[
        "ignore previous instructions",
        "pretend you are",
        "you are now",
        "do not follow",
        "bypass your programming"
    ]
)
```

### Moderation Logging and Analytics

```python
from agents_hub.monitoring import LangfuseMonitor

# Create a Langfuse monitor
monitor = LangfuseMonitor(
    public_key="your-langfuse-public-key",
    secret_key="your-langfuse-secret-key"
)

# Create agent with moderation and monitoring
agent = Agent(
    name="monitored_agent",
    llm=llm,
    moderation=combined_moderator,
    monitor=monitor,
    on_moderation_violation="log"
)

# Moderation events will be logged to Langfuse
```

## Ethical Considerations

The moderation module is designed with these ethical principles in mind:
- **Transparency**: Clear communication about moderation decisions
- **Fairness**: Avoiding bias in content filtering
- **Privacy**: Minimizing data collection and storage
- **Proportionality**: Appropriate responses to different types of content
- **User Agency**: Providing options for users to understand and appeal moderation decisions
