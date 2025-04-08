# Monitoring Module for Agents Hub

This module provides monitoring and observability capabilities for the Agents Hub framework, allowing you to track agent performance, analyze conversations, and gather insights about your agent systems.

## Components

### Monitors

The module includes several monitor implementations:
- **LangfuseMonitor**: Integrates with Langfuse for comprehensive monitoring and analytics
- **ConsoleMonitor**: Simple monitoring with console output for development
- **CustomMonitor**: Base class for creating custom monitoring solutions

### Tracked Metrics

The monitoring system can track various metrics:
- **Latency**: Response time for agent operations
- **Token Usage**: Number of tokens consumed by LLM calls
- **Cost**: Estimated cost of LLM usage
- **Success Rate**: Percentage of successful agent operations
- **User Satisfaction**: Feedback scores from users
- **Tool Usage**: Frequency and success of tool operations
- **Moderation Events**: Content moderation actions and violations

## Usage

### Creating Monitors

```python
from agents_hub.monitoring import LangfuseMonitor, ConsoleMonitor

# Langfuse monitor
langfuse_monitor = LangfuseMonitor(
    public_key="your-langfuse-public-key",
    secret_key="your-langfuse-secret-key",
    host="https://cloud.langfuse.com",  # Optional
    release="1.0.0",  # Optional version tracking
)

# Console monitor for development
console_monitor = ConsoleMonitor(
    log_level="INFO",
    include_timestamps=True
)
```

### Using Monitoring with Agents

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create agent with monitoring
agent = Agent(
    name="monitored_agent",
    llm=llm,
    monitor=langfuse_monitor,
    system_prompt="You are a helpful assistant."
)

# The agent will now automatically track all operations
```

### Tracking Conversations

```python
# Use the agent with conversation tracking
response = await agent.run(
    "What is the capital of France?",
    context={
        "conversation_id": "user123",
        "user_id": "user456",
        "session_id": "session789"
    }
)

# Score a conversation
await langfuse_monitor.score_conversation(
    conversation_id="user123",
    name="helpfulness",
    value=0.9,
    comment="Very helpful response"
)

# Add user feedback
await langfuse_monitor.add_user_feedback(
    conversation_id="user123",
    score=5,  # 1-5 scale
    comment="The agent was very helpful and provided exactly what I needed."
)
```

### Custom Events

```python
# Track custom events
await langfuse_monitor.track_event(
    name="user_signup",
    properties={
        "user_id": "user456",
        "plan": "premium",
        "referral_source": "google"
    }
)

# Track errors
try:
    # Some operation that might fail
    result = await some_operation()
except Exception as e:
    await langfuse_monitor.track_error(
        error=e,
        context={
            "operation": "some_operation",
            "user_id": "user456"
        }
    )
```

## Advanced Features

### Custom Monitors

You can create custom monitors by extending the BaseMonitor class:

```python
from agents_hub.monitoring.base import BaseMonitor

class CustomMonitor(BaseMonitor):
    def __init__(self, api_key: str, endpoint: str):
        super().__init__(name="custom_monitor")
        self.api_key = api_key
        self.endpoint = endpoint
    
    async def track_llm_call(self, **kwargs):
        # Implement your custom tracking logic
        await self._send_data("llm_call", kwargs)
    
    async def track_agent_run(self, **kwargs):
        # Implement your custom tracking logic
        await self._send_data("agent_run", kwargs)
    
    async def _send_data(self, event_type, data):
        # Your custom implementation to send data to your monitoring system
        pass
```

### Monitoring Dashboards

With Langfuse, you can access comprehensive dashboards for:
- **Usage Analytics**: Track token usage, costs, and request volumes
- **Performance Metrics**: Monitor latency, success rates, and errors
- **Conversation Analysis**: Analyze conversation flows and user interactions
- **User Feedback**: Track user satisfaction and feedback trends
- **Custom Reports**: Create custom reports and visualizations

### Alerting and Notifications

```python
# Set up alerts for specific conditions
await langfuse_monitor.create_alert(
    name="high_error_rate",
    condition="error_rate > 0.05",  # 5% error rate
    channels=["email", "slack"],
    recipients=["alerts@example.com", "#monitoring-channel"]
)
```

## Integration with Other Modules

The monitoring module integrates with:
- **Moderation Module**: Track moderation events and violations
- **Memory Module**: Monitor memory usage and retrieval performance
- **Tools Module**: Track tool usage and success rates
- **RAG Module**: Monitor retrieval performance and relevance

## Data Privacy

The monitoring module is designed with privacy in mind:
- **Data Minimization**: Only track essential information
- **Anonymization**: Option to anonymize user identifiers
- **Retention Policies**: Configure data retention periods
- **Access Controls**: Restrict access to monitoring data
