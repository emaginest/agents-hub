# Monitoring in Agents Hub

Agents Hub provides a comprehensive monitoring system that allows you to track agent interactions, tool usage, and performance metrics. This documentation explains how to use the monitoring system with Langfuse integration.

## Overview

The monitoring system in Agents Hub is designed to:

1. **Track Conversations**: Monitor user and assistant messages
2. **Track Tool Usage**: Monitor tool calls and their results
3. **Track LLM Calls**: Monitor calls to language models
4. **Track Errors**: Monitor errors and exceptions
5. **Score Conversations**: Evaluate conversation quality

The monitoring system is built on a flexible architecture that allows for different monitoring backends. Currently, Agents Hub supports Langfuse as a monitoring backend.

## Langfuse Integration

[Langfuse](https://langfuse.com/) is an open-source observability and analytics platform for LLM applications. It provides a comprehensive set of tools for monitoring, debugging, and analyzing LLM-powered applications.

### Setting Up Langfuse

To use Langfuse with Agents Hub, you need to:

1. **Create a Langfuse Account**: Sign up at [cloud.langfuse.com](https://cloud.langfuse.com)
2. **Get API Keys**: Create a project and get your public and secret API keys
3. **Set Environment Variables**:
   ```
   LANGFUSE_PUBLIC_KEY=your-public-key
   LANGFUSE_SECRET_KEY=your-secret-key
   LANGFUSE_HOST=https://cloud.langfuse.com  # Optional, defaults to cloud.langfuse.com
   ```

### Creating a Langfuse Monitor

```python
from agents_hub.monitoring import LangfuseMonitor

# Create a Langfuse monitor
monitor = LangfuseMonitor(
    public_key="your-public-key",
    secret_key="your-secret-key",
    host="https://cloud.langfuse.com",  # Optional
    release="1.0.0",  # Optional version tracking
    debug=True,  # Optional debug mode
    redact_pii=True,  # Optional PII redaction
)
```

### Using the Monitor with an Agent

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.monitoring import LangfuseMonitor

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create Langfuse monitor
monitor = LangfuseMonitor(
    public_key="your-langfuse-public-key",
    secret_key="your-langfuse-secret-key",
)

# Create agent with monitoring
agent = Agent(
    name="monitored_agent",
    llm=llm,
    monitor=monitor,
)

# Use the agent
response = await agent.run(
    "What is the capital of France?",
    context={"conversation_id": "user123"},
)
```

### Monitoring Levels

You can control the level of monitoring with the `level` parameter:

```python
from agents_hub.monitoring import LangfuseMonitor, MonitoringLevel

# Create a Langfuse monitor with basic monitoring
monitor = LangfuseMonitor(
    public_key="your-public-key",
    secret_key="your-secret-key",
    level=MonitoringLevel.BASIC,  # Only track basic events
)

# Create a Langfuse monitor with detailed monitoring
monitor = LangfuseMonitor(
    public_key="your-public-key",
    secret_key="your-secret-key",
    level=MonitoringLevel.DETAILED,  # Track detailed events (default)
)

# Create a Langfuse monitor with comprehensive monitoring
monitor = LangfuseMonitor(
    public_key="your-public-key",
    secret_key="your-secret-key",
    level=MonitoringLevel.COMPREHENSIVE,  # Track all events
)
```

### Including and Excluding Events

You can include or exclude specific events:

```python
from agents_hub.monitoring import LangfuseMonitor, MonitoringEvent

# Create a Langfuse monitor with specific events
monitor = LangfuseMonitor(
    public_key="your-public-key",
    secret_key="your-secret-key",
    include_events=[
        MonitoringEvent.USER_MESSAGE,
        MonitoringEvent.ASSISTANT_MESSAGE,
        MonitoringEvent.TOOL_CALL,
    ],
)

# Create a Langfuse monitor excluding specific events
monitor = LangfuseMonitor(
    public_key="your-public-key",
    secret_key="your-secret-key",
    exclude_events=[
        MonitoringEvent.LLM_CALL,
        MonitoringEvent.LLM_RESULT,
    ],
)
```

### Scoring Conversations

You can score conversations for quality evaluation:

```python
# Score a conversation
await monitor.score_conversation(
    conversation_id="user123",
    name="helpfulness",
    value=0.9,
    comment="Very helpful response",
)
```

## Monitoring Registry

You can use multiple monitors with the `MonitoringRegistry`:

```python
from agents_hub.monitoring import LangfuseMonitor, MonitoringRegistry

# Create monitors
langfuse_monitor = LangfuseMonitor(
    public_key="your-langfuse-public-key",
    secret_key="your-langfuse-secret-key",
)

# Create a monitoring registry
registry = MonitoringRegistry(
    monitors=[langfuse_monitor],
)

# Create agent with monitoring registry
agent = Agent(
    name="monitored_agent",
    llm=llm,
    monitor=registry,
)
```

## Monitoring Events

The monitoring system tracks the following events:

- **CONVERSATION_START**: Start of a conversation
- **CONVERSATION_END**: End of a conversation
- **USER_MESSAGE**: User message
- **ASSISTANT_MESSAGE**: Assistant message
- **TOOL_CALL**: Tool call
- **TOOL_RESULT**: Tool result
- **MEMORY_READ**: Memory read operation
- **MEMORY_WRITE**: Memory write operation
- **LLM_CALL**: LLM call
- **LLM_RESULT**: LLM result
- **ERROR**: Error or exception
- **CUSTOM**: Custom event

## PII Redaction

The Langfuse monitor includes PII (Personally Identifiable Information) redaction to protect sensitive data:

```python
# Create a Langfuse monitor with PII redaction
monitor = LangfuseMonitor(
    public_key="your-public-key",
    secret_key="your-secret-key",
    redact_pii=True,  # Enable PII redaction (default)
)
```

The PII redaction system currently detects and redacts:
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers

## Viewing Monitoring Data

You can view your monitoring data in the Langfuse dashboard:

1. Go to [cloud.langfuse.com](https://cloud.langfuse.com)
2. Log in to your account
3. Select your project
4. View traces, spans, and scores

The dashboard provides:
- Conversation traces
- Message history
- Tool usage
- LLM calls
- Error logs
- Performance metrics

## FastAPI Integration

You can integrate monitoring with a FastAPI application:

```python
from fastapi import FastAPI
from agents_hub.monitoring import LangfuseMonitor

app = FastAPI()
monitor = None

@app.on_event("startup")
async def startup_event():
    global monitor
    
    # Initialize Langfuse monitoring
    if all([
        os.environ.get("LANGFUSE_PUBLIC_KEY"),
        os.environ.get("LANGFUSE_SECRET_KEY"),
    ]):
        monitor = LangfuseMonitor(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
        )
    
    # Create agent with monitoring
    agent = Agent(
        name="api_agent",
        llm=llm,
        monitor=monitor,
    )

@app.post("/chat")
async def chat(request: ChatRequest):
    # Use the agent with monitoring
    response = await agent.run(
        request.message,
        context={"conversation_id": request.user_id},
    )
    
    return {"response": response}
```

## Best Practices

1. **Use Consistent Conversation IDs**: Use consistent conversation IDs to track conversations across multiple interactions.
2. **Include Metadata**: Include relevant metadata in context to provide additional information for monitoring.
3. **Score Conversations**: Use scoring to evaluate conversation quality and track improvements.
4. **Monitor Performance**: Use monitoring data to identify performance bottlenecks and optimize your agents.
5. **Protect PII**: Enable PII redaction to protect sensitive user data.

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Make sure you have set the `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` environment variables.
2. **Connection Issues**: Check your internet connection and firewall settings.
3. **Rate Limiting**: If you're experiencing rate limiting, consider reducing the monitoring level or excluding some events.
4. **Missing Data**: Make sure you're passing conversation IDs in the context.

### Debugging

To debug monitoring issues, you can enable debug mode:

```python
monitor = LangfuseMonitor(
    public_key="your-public-key",
    secret_key="your-secret-key",
    debug=True,
)
```

You can also enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Resources

- [Langfuse Documentation](https://langfuse.com/docs)
- [Langfuse GitHub Repository](https://github.com/langfuse/langfuse)
- [Langfuse Python SDK](https://github.com/langfuse/langfuse-python)
