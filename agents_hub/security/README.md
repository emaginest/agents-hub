# Security Module for Agents Hub

This module provides security features for the Agents Hub framework, ensuring that agent systems operate safely, ethically, and in compliance with relevant standards.

## Components

### Ethics

The ethics directory contains components for ethical AI:
- **EthicalGuidelines**: Define ethical boundaries for agents
- **ValueAlignment**: Ensure agent behavior aligns with human values
- **FairnessEvaluator**: Detect and mitigate bias in agent responses

### Authentication

The authentication components provide secure access control:
- **APIKeyManager**: Securely manage and rotate API keys
- **TokenValidator**: Validate authentication tokens
- **PermissionChecker**: Enforce permission-based access control

### Data Protection

The data protection components ensure sensitive information is handled properly:
- **DataSanitizer**: Remove sensitive information from text
- **PII Detector**: Identify personally identifiable information
- **Encryption**: Encrypt sensitive data

## Usage

### Ethical Guidelines

```python
from agents_hub.security.ethics import EthicalGuidelines
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create ethical guidelines
guidelines = EthicalGuidelines(
    principles=[
        "Respect user privacy and confidentiality",
        "Provide accurate and truthful information",
        "Avoid harmful or discriminatory content",
        "Be transparent about limitations",
        "Prioritize user safety and wellbeing"
    ],
    prohibited_topics=["illegal activities", "harmful content"],
    value_alignment="human_centered"
)

# Create agent with ethical guidelines
agent = Agent(
    name="ethical_assistant",
    llm=llm,
    system_prompt="You are a helpful assistant that follows ethical guidelines.",
    security_config={
        "ethical_guidelines": guidelines
    }
)

# The agent will now follow the ethical guidelines in its responses
response = await agent.run("How can I make a lot of money quickly?")
print(response)  # Will provide ethical advice only
```

### API Key Management

```python
from agents_hub.security.authentication import APIKeyManager

# Create API key manager
key_manager = APIKeyManager(
    storage_type="encrypted_file",
    storage_path="./api_keys.enc",
    encryption_key="your-encryption-key"
)

# Add API keys
await key_manager.add_key(
    provider="openai",
    key="your-openai-api-key",
    metadata={
        "owner": "admin",
        "created_at": "2023-06-15T14:30:00Z",
        "expires_at": "2024-06-15T14:30:00Z"
    }
)

# Get API key
openai_key = await key_manager.get_key("openai")

# Rotate API key
await key_manager.rotate_key(
    provider="openai",
    new_key="your-new-openai-api-key"
)

# Use with LLM provider
from agents_hub.llm.providers import OpenAIProvider

llm = OpenAIProvider(
    api_key=await key_manager.get_key("openai")
)
```

### Data Protection

```python
from agents_hub.security.data_protection import DataSanitizer, PIIDetector

# Create PII detector
pii_detector = PIIDetector(
    detection_types=["email", "phone", "address", "name", "ssn", "credit_card"],
    confidence_threshold=0.7
)

# Create data sanitizer
data_sanitizer = DataSanitizer(
    pii_detector=pii_detector,
    replacement_strategy="mask",  # Options: mask, redact, pseudonymize
    preserve_format=True
)

# Sanitize text
original_text = "My name is John Doe, my email is john.doe@example.com, and my phone is 555-123-4567."
sanitized_text = await data_sanitizer.sanitize(original_text)
print(sanitized_text)  # "My name is [NAME], my email is [EMAIL], and my phone is [PHONE]."

# Use with agent
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider

llm = OpenAIProvider(api_key="your-openai-api-key")

agent = Agent(
    name="privacy_conscious_assistant",
    llm=llm,
    system_prompt="You are a helpful assistant that respects user privacy.",
    security_config={
        "data_sanitizer": data_sanitizer,
        "sanitize_inputs": True,
        "sanitize_outputs": True
    }
)

# The agent will automatically sanitize inputs and outputs
response = await agent.run("My name is Jane Smith and my email is jane.smith@example.com. Can you help me?")
print(response)  # Will not repeat the PII in the response
```

## Advanced Features

### Fairness Evaluation

```python
from agents_hub.security.ethics import FairnessEvaluator
from agents_hub.monitoring import LangfuseMonitor

# Initialize monitoring
monitor = LangfuseMonitor(
    public_key="your-langfuse-public-key",
    secret_key="your-langfuse-secret-key"
)

# Create fairness evaluator
fairness_evaluator = FairnessEvaluator(
    bias_categories=["gender", "race", "age", "religion", "nationality"],
    evaluation_frequency=0.1,  # Evaluate 10% of responses
    monitor=monitor
)

# Create agent with fairness evaluation
from agents_hub import Agent
from agents_hub.llm.providers import ClaudeProvider

llm = ClaudeProvider(api_key="your-anthropic-api-key")

agent = Agent(
    name="fair_assistant",
    llm=llm,
    system_prompt="You are a helpful assistant that provides fair and unbiased responses.",
    security_config={
        "fairness_evaluator": fairness_evaluator
    },
    monitor=monitor
)

# The agent will periodically evaluate responses for fairness
response = await agent.run("What makes a good leader?")
print(response)

# Check fairness evaluation results
evaluation_results = await fairness_evaluator.get_evaluation_results(
    agent_id="fair_assistant",
    time_period="last_7_days"
)
print(evaluation_results)
```

### Secure Multi-Agent Systems

```python
from agents_hub import AgentWorkforce, Agent
from agents_hub.security.authentication import PermissionChecker
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create permission checker
permission_checker = PermissionChecker(
    permission_model="role_based",
    roles={
        "researcher": ["search", "read"],
        "analyst": ["search", "read", "analyze"],
        "manager": ["search", "read", "analyze", "write", "approve"]
    }
)

# Create agents with different permissions
researcher = Agent(
    name="researcher",
    llm=llm,
    system_prompt="You are a researcher who finds information.",
    security_config={
        "permission_checker": permission_checker,
        "role": "researcher"
    }
)

analyst = Agent(
    name="analyst",
    llm=llm,
    system_prompt="You are an analyst who evaluates information.",
    security_config={
        "permission_checker": permission_checker,
        "role": "analyst"
    }
)

manager = Agent(
    name="manager",
    llm=llm,
    system_prompt="You are a manager who makes decisions.",
    security_config={
        "permission_checker": permission_checker,
        "role": "manager"
    }
)

# Create a workforce with these agents
workforce = AgentWorkforce(
    agents=[researcher, analyst, manager],
    security_config={
        "permission_checker": permission_checker,
        "enforce_permissions": True
    }
)

# The workforce will enforce permissions for each agent
result = await workforce.execute(
    "Research the market trends, analyze the data, and approve the marketing strategy."
)
```

## Integration with Other Modules

The security module integrates with:
- **Moderation Module**: For content filtering and safety
- **Monitoring Module**: For tracking security events
- **Memory Module**: For secure storage of information
- **Tools Module**: For secure tool usage
- **Orchestration Module**: For secure agent collaboration
