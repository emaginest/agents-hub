# Tools Module for Agents Hub

This module provides a collection of tools that agents can use to interact with external systems, process data, and perform specialized tasks.

## Tool Categories

### Standard Tools

- **ScraperTool**: Scrape and extract content from websites
- **PGVectorTool**: Store and retrieve vector embeddings in PostgreSQL
- **TavilyTool**: Search the web and extract content using Tavily API
- **MCPTool**: Connect to Model Context Protocol servers for filesystem, GitHub, etc.
- **CalculatorTool**: Perform mathematical calculations
- **WebSearchTool**: Search the web for information
- **WebFetchTool**: Fetch and parse web content

### Coding Tools

- **GitTool**: Perform Git operations with human approval for critical actions
- **AWSCDKTool**: Manage AWS CDK operations with human approval for deployments
- **CodeGeneratorTool**: Generate code based on specifications
- **CodeAnalyzerTool**: Analyze code quality and structure
- **TestingTool**: Run tests and analyze test results

### Connectors

- **DatabaseConnector**: Connect to various database systems
- **APIConnector**: Connect to external APIs
- **FileSystemConnector**: Access and manipulate files

## Usage

### Using Tools with Agents

```python
from agents_hub import Agent
from agents_hub.tools.standard import WebSearchTool, ScraperTool
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Initialize tools
web_search = WebSearchTool()
scraper = ScraperTool()

# Create agent with tools
agent = Agent(
    name="researcher",
    llm=llm,
    tools=[web_search, scraper],
    system_prompt="You are a research assistant that can search the web and extract information."
)

# Use the agent with tools
response = await agent.run("Research the latest developments in quantum computing")
```

### Creating Custom Tools

You can create custom tools by extending the BaseTool class:

```python
from agents_hub.tools.base import BaseTool
from typing import Dict, Any, Optional

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="A custom tool for specific tasks",
            parameters={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter",
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Second parameter",
                    },
                },
                "required": ["param1"],
            },
        )
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        # Implement tool functionality
        param1 = parameters.get("param1")
        param2 = parameters.get("param2", 0)
        
        # Process parameters and return result
        return {
            "status": "success",
            "result": f"Processed {param1} with value {param2}",
        }
```

## Tool Registry

The ToolRegistry allows you to register and manage tools:

```python
from agents_hub.tools import ToolRegistry
from agents_hub.tools.standard import WebSearchTool, ScraperTool

# Create tool registry
registry = ToolRegistry()

# Register tools
registry.register(WebSearchTool())
registry.register(ScraperTool())

# Get tool by name
web_search = registry.get_tool("web_search")

# Get all tools
all_tools = registry.get_all_tools()

# Create agent with all registered tools
agent = Agent(
    name="multi_tool_agent",
    llm=llm,
    tools=registry.get_all_tools(),
    system_prompt="You are an assistant with access to multiple tools."
)
```

## Human Approval

Some tools, like GitTool and AWSCDKTool, include human approval mechanisms for critical operations:

```python
from agents_hub.tools.coding import GitTool
from agents_hub.utils.approval import ApprovalInterface

# Create approval interface
approval_interface = ApprovalInterface()

# Create Git tool
git_tool = GitTool()

# Use the tool (will request approval for push operation)
result = await git_tool.run({
    "operation": "push",
    "path": "/path/to/repository",
    "remote": "origin",
    "branch": "main",
})
```

## Tool Chaining

Tools can be chained together to perform complex operations:

```python
# Search for information
search_result = await web_search.run({
    "query": "Latest quantum computing breakthroughs",
})

# Extract content from the top result
url = search_result["results"][0]["url"]
content_result = await scraper.run({
    "url": url,
})

# Process the extracted content
processed_content = content_result["content"]
```
