# Tavily Search API in Agents Hub

Agents Hub provides integration with the Tavily Search API, allowing agents to search the web for information and extract content from web pages.

## Overview

The Tavily integration in Agents Hub offers two main capabilities:

1. **Web Search**: Search the web for information on any topic
2. **Content Extraction**: Extract and process content from specific URLs

These capabilities are available through:

1. **Standard Tool**: The `TavilyTool` class for direct API access
2. **MCP Integration**: The Model Context Protocol server for Tavily

## Getting Started

### Prerequisites

To use the Tavily integration, you need:

1. A Tavily API key (sign up at [tavily.com](https://tavily.com))
2. The `tavily-python` package (included in Agents Hub dependencies)

### Setting Up

Set your Tavily API key as an environment variable:

```bash
# Linux/macOS
export TAVILY_API_KEY=your-api-key

# Windows (PowerShell)
$env:TAVILY_API_KEY="your-api-key"
```

Or provide it directly when creating the tool:

```python
from agents_hub.tools.standard import TavilyTool

tavily_tool = TavilyTool(api_key="your-api-key")
```

## Using the Tavily Tool

### Basic Search

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import TavilyTool

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create Tavily tool
tavily_tool = TavilyTool(api_key="your-tavily-api-key")

# Create agent with Tavily tool
agent = Agent(
    name="research_agent",
    llm=llm,
    tools=[tavily_tool],
    system_prompt="You are a research assistant that can search the web for information.",
)

# Use the agent to search for information
response = await agent.run("What are the latest developments in quantum computing?")
```

### Advanced Configuration

The `TavilyTool` class supports various configuration options:

```python
tavily_tool = TavilyTool(
    api_key="your-tavily-api-key",
    search_depth="advanced",  # "basic" or "advanced"
    max_results=10,  # Number of results to return
    include_domains=["edu", "gov"],  # Only include these domains
    exclude_domains=["example.com"],  # Exclude these domains
)
```

### Content Extraction

You can extract content from specific URLs:

```python
# The agent will automatically use the extract operation when given a URL
response = await agent.run("Extract and summarize the content from this URL: https://example.com")
```

## Tavily MCP Integration

Agents Hub also supports the Tavily MCP server for more advanced integration:

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import MCPTool

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create MCP tool for Tavily
tavily_tool = MCPTool(
    server_name="tavily",
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-tavily"],
    server_env={"TAVILY_API_KEY": "your-tavily-api-key"},
    transport="stdio",
)

# Create agent with Tavily MCP tool
agent = Agent(
    name="tavily_agent",
    llm=llm,
    tools=[tavily_tool],
    system_prompt="You are an assistant that can search the web using Tavily.",
)

# Use the agent to search for information
response = await agent.run("What are the latest developments in quantum computing?")
```

## Tool Parameters

### Search Operation

When using the search operation, you can provide the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `operation` | string | Set to `"search"` for search operation |
| `query` | string | The search query |
| `search_depth` | string | Search depth (`"basic"` or `"advanced"`) |
| `max_results` | integer | Maximum number of results to return |
| `include_domains` | array | List of domains to include in search |
| `exclude_domains` | array | List of domains to exclude from search |
| `include_answer` | boolean | Whether to include an answer in search results |
| `include_raw_content` | boolean | Whether to include raw content in search results |

Example:

```python
result = await tavily_tool.run({
    "operation": "search",
    "query": "What are the latest developments in quantum computing?",
    "search_depth": "advanced",
    "max_results": 10,
    "include_domains": ["edu", "gov"],
    "exclude_domains": ["example.com"],
    "include_answer": True,
    "include_raw_content": False,
}, {})
```

### Extract Operation

When using the extract operation, you can provide the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `operation` | string | Set to `"extract"` for extract operation |
| `url` | string | The URL to extract content from |
| `extract_type` | string | Type of extraction (`"text"` or `"structured"`) |

Example:

```python
result = await tavily_tool.run({
    "operation": "extract",
    "url": "https://example.com",
    "extract_type": "text",
}, {})
```

## Best Practices

### Effective Searching

1. **Be Specific**: Use specific search queries for better results
2. **Use Advanced Depth**: For comprehensive research, use `search_depth="advanced"`
3. **Filter Domains**: Use `include_domains` and `exclude_domains` to focus on reliable sources
4. **Limit Results**: Use `max_results` to control the number of results

### Content Extraction

1. **Check URL Validity**: Ensure the URL is valid and accessible
2. **Choose Extraction Type**: Use `extract_type="text"` for general content and `extract_type="structured"` for structured data
3. **Process Large Content**: For large web pages, consider processing the content in chunks

### Agent Prompting

1. **Clear Instructions**: Provide clear instructions for the agent on what information to search for
2. **Specify Sources**: When appropriate, specify preferred sources or domains
3. **Request Citations**: Ask the agent to cite sources in its response

## Use Cases

### Data Enrichment

Enrich data with information from the web:

```python
prompt = """
I need to enrich data for iPhone 13. Please find and provide the following information:
1. Technical specifications
2. Current market price range
3. Key features
4. Main competitors
5. Recent reviews or ratings

Format the information in a structured way.
"""

response = await agent.run(prompt)
```

### Company Research

Research companies and organizations:

```python
prompt = """
I need comprehensive research on Microsoft. Please provide:
1. Company overview and history
2. Main products and services
3. Recent financial performance
4. Key executives
5. Major competitors
6. Recent news or developments

Organize the information in a clear, structured format.
"""

response = await agent.run(prompt)
```

### Web Evaluation

Evaluate websites and web content:

```python
prompt = """
Please evaluate the website https://www.who.int based on the following criteria:
1. Content quality and reliability
2. User experience and navigation
3. Mobile responsiveness
4. Loading speed
5. Accessibility features
6. Security measures

Provide a detailed analysis with specific examples.
"""

response = await agent.run(prompt)
```

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure your Tavily API key is valid and properly set
2. **Rate Limiting**: Tavily has rate limits; if you hit them, consider implementing retries
3. **Search Quality**: If search results are poor, try refining the query or using advanced search depth
4. **Extraction Failures**: Some websites block extraction; try different URLs or approaches

### Error Handling

The Tavily tool includes error handling for common issues:

```python
result = await tavily_tool.run({
    "operation": "search",
    "query": "What are the latest developments in quantum computing?",
}, {})

if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Search results: {result}")
```

## Resources

- [Tavily API Documentation](https://docs.tavily.com/documentation/about)
- [Tavily Python SDK](https://pypi.org/project/tavily-python/)
- [Tavily MCP Documentation](https://docs.tavily.com/documentation/mcp)
- [Tavily Best Practices](https://docs.tavily.com/documentation/best-practices/best-practices-search)
