# Long-Term Memory Example

This example demonstrates how to use PostgreSQL for long-term memory in agents-hub. It shows how to create an agent that remembers past conversations across multiple sessions.

## Features

- PostgreSQL-based persistent memory
- Conversation history that persists across sessions
- Memory search functionality
- Support for multiple LLM providers (OpenAI, Anthropic, Ollama)

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- API keys for your preferred LLM provider (OpenAI, Anthropic, or Ollama running locally)

## Setup

### 1. Start PostgreSQL with Docker

```bash
# From the memory_example directory
docker-compose up -d
```

This will start a PostgreSQL database with the necessary tables for memory storage.

### 2. Set up environment variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit the `.env` file to add your API keys and adjust any other settings.

### 3. Install dependencies

```bash
pip install -e ../../  # Install agents-hub
pip install -r requirements.txt

# Optional: Install python-Levenshtein to remove fuzzywuzzy warning
pip install python-Levenshtein
```

> **Note**: You might see a warning about `fuzzywuzzy` using a slow pure-python SequenceMatcher. This is harmless and can be resolved by installing the optional `python-Levenshtein` package as shown above.

## Usage

### Basic Usage

Run the example with your preferred LLM provider:

```bash
# Use OpenAI (default)
python memory_test.py

# Use Anthropic
python memory_test.py --llm anthropic

# Use Ollama (local)
python memory_test.py --llm ollama
```

### Continuing a Conversation

To continue a previous conversation, use the `--conversation` flag with the conversation ID:

```bash
python memory_test.py --conversation 123e4567-e89b-12d3-a456-426614174000
```

The conversation ID is displayed when you start a new conversation.

### Clearing Memory

To clear the memory for a conversation:

```bash
python memory_test.py --conversation 123e4567-e89b-12d3-a456-426614174000 --clear
```

## Interactive Commands

During the conversation, you can use these special commands:

- `exit` - End the conversation
- `stats` - Show memory statistics
- `history` - Show conversation history
- `search <query>` - Search memory for a specific query

## How It Works

1. The example initializes a PostgreSQL memory backend that connects to the database
2. It creates an agent with this memory backend
3. When you chat with the agent, all interactions are stored in the database
4. The agent can access past conversations to provide context-aware responses
5. The memory persists even after you exit the program, allowing for true long-term memory

## Customization

You can customize the example by:

- Modifying the system prompt in `memory_test.py`
- Adjusting PostgreSQL connection parameters in `.env`
- Changing the LLM model in `.env`
