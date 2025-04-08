# LLM Module for Agents Hub

This module provides a unified interface for interacting with various Large Language Model (LLM) providers, allowing agents to use different models based on their specific needs.

## Components

### Base LLM Interface

The BaseLLM class defines a standard interface for all LLM providers:
- **Completion**: Generate text completions
- **Chat**: Generate conversational responses
- **Embeddings**: Generate vector embeddings for text
- **Streaming**: Stream responses for real-time interaction
- **Function Calling**: Use model to call functions

### Providers

The module supports multiple LLM providers:
- **OpenAIProvider**: Access to GPT models (GPT-4o, GPT-4, GPT-3.5-Turbo)
- **ClaudeProvider**: Access to Anthropic's Claude models (Claude 3 Opus, Sonnet, Haiku)
- **GeminiProvider**: Access to Google's Gemini models
- **OllamaProvider**: Access to locally hosted models via Ollama
- **AzureOpenAIProvider**: Access to Azure-hosted OpenAI models
- **HuggingFaceProvider**: Access to models hosted on Hugging Face

## Usage

### Creating LLM Providers

```python
from agents_hub.llm.providers import OpenAIProvider, ClaudeProvider, GeminiProvider, OllamaProvider

# OpenAI
openai_llm = OpenAIProvider(
    api_key="your-openai-api-key",
    model="gpt-4o",  # Default model
    temperature=0.7,
    max_tokens=1000
)

# Anthropic Claude
claude_llm = ClaudeProvider(
    api_key="your-anthropic-api-key",
    model="claude-3-opus-20240229",  # Default model
    temperature=0.5,
    max_tokens=2000
)

# Google Gemini
gemini_llm = GeminiProvider(
    api_key="your-google-api-key",
    model="gemini-pro",  # Default model
    temperature=0.8,
    max_tokens=1500
)

# Ollama (local models)
ollama_llm = OllamaProvider(
    model="llama3",  # Default model
    host="http://localhost:11434",
    temperature=0.7,
    max_tokens=1000
)
```

### Using LLMs for Completion

```python
# Generate text completion
completion = await openai_llm.complete(
    prompt="Write a short poem about artificial intelligence.",
    temperature=0.8,  # Override default temperature
    max_tokens=200    # Override default max_tokens
)

print(completion.text)
print(f"Token usage: {completion.usage.total_tokens}")
```

### Using LLMs for Chat

```python
# Generate chat response
chat_response = await claude_llm.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(chat_response.message.content)
print(f"Token usage: {chat_response.usage.total_tokens}")
```

### Streaming Responses

```python
# Stream chat response
async for chunk in claude_llm.stream_chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ]
):
    print(chunk.message.content, end="", flush=True)
```

### Generating Embeddings

```python
# Generate embeddings
embeddings = await openai_llm.get_embeddings(
    texts=["This is a sample text.", "This is another sample."]
)

print(f"Embedding dimensions: {len(embeddings[0])}")
```

### Function Calling

```python
# Define functions
functions = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The temperature unit"
                }
            },
            "required": ["location"]
        }
    }
]

# Use function calling
response = await openai_llm.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the weather like in New York?"}
    ],
    functions=functions,
    function_call="auto"
)

if response.message.function_call:
    function_name = response.message.function_call.name
    function_args = response.message.function_call.arguments
    print(f"Function: {function_name}")
    print(f"Arguments: {function_args}")
```

## Advanced Features

### Model Selection

```python
# Create provider with multiple models
openai_provider = OpenAIProvider(
    api_key="your-openai-api-key",
    models={
        "default": "gpt-4o",
        "fast": "gpt-3.5-turbo",
        "powerful": "gpt-4-turbo"
    }
)

# Use different models for different tasks
fast_response = await openai_provider.chat(
    messages=[{"role": "user", "content": "Quick summary of photosynthesis?"}],
    model="fast"
)

detailed_response = await openai_provider.chat(
    messages=[{"role": "user", "content": "Detailed analysis of quantum computing applications?"}],
    model="powerful"
)
```

### Fallback Mechanisms

```python
from agents_hub.llm import LLMWithFallback

# Create a provider with fallback
fallback_llm = LLMWithFallback(
    primary=openai_llm,
    fallbacks=[claude_llm, gemini_llm],
    max_retries=3
)

# If the primary provider fails, it will automatically try the fallbacks
response = await fallback_llm.chat(
    messages=[{"role": "user", "content": "What is the meaning of life?"}]
)
```

### Caching

```python
from agents_hub.llm import CachedLLM

# Create a cached LLM provider
cached_llm = CachedLLM(
    llm=openai_llm,
    cache_type="redis",
    cache_config={
        "host": "localhost",
        "port": 6379,
        "ttl": 3600  # Cache for 1 hour
    }
)

# Responses will be cached based on input
response1 = await cached_llm.chat(
    messages=[{"role": "user", "content": "What is the capital of France?"}]
)

# This will use the cached response if available
response2 = await cached_llm.chat(
    messages=[{"role": "user", "content": "What is the capital of France?"}]
)
```

## Integration with Other Modules

The LLM module integrates with:
- **Monitoring Module**: For tracking LLM usage and performance
- **Memory Module**: For generating embeddings for memory storage
- **Moderation Module**: For content filtering
- **Tools Module**: For function calling capabilities
