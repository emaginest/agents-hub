# Tools Module for Agents Hub

This module provides a collection of tools that agents can use to interact with external systems, process data, and perform specialized tasks.

## Tool Categories

### Standard Tools

- **ScraperTool**: Scrape and extract content from websites
- **PlaywrightScraperTool**: Advanced web scraping with Playwright for JavaScript-heavy websites
- **CalculatorTool**: Perform mathematical calculations
- **WebSearchTool**: Search the web for information
- **WebFetchTool**: Fetch and parse web content
- **MCPTool**: Connect to MCP (Model Context Protocol) servers using either SSE or stdio transport

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
from agents_hub.tools.standard import WebSearchTool, ScraperTool, PlaywrightScraperTool
from agents_hub.llm.providers import OpenAIProvider

# Initialize LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Initialize tools
web_search = WebSearchTool()
scraper = ScraperTool()
playwright_scraper = PlaywrightScraperTool()

# Create agent with tools
agent = Agent(
    name="researcher",
    llm=llm,
    tools=[web_search, scraper, playwright_scraper],
    system_prompt="You are a research assistant that can search the web and extract information from any website."
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
from agents_hub.tools.standard import WebSearchTool, ScraperTool, PlaywrightScraperTool

# Create tool registry
registry = ToolRegistry()

# Register tools
registry.register(WebSearchTool())
registry.register(ScraperTool())
registry.register(PlaywrightScraperTool())

# Get tool by name
web_search = registry.get_tool("web_search")
playwright_scraper = registry.get_tool("playwright_scraper")

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

# For static websites, use the regular scraper
content_result = await scraper.run({
    "url": url,
})

# For JavaScript-heavy websites, use the Playwright scraper
js_content_result = await playwright_scraper.run({
    "url": url,
    "wait_for_selector": ".main-content",
    "stealth_mode": True,
})

# Process the extracted content
processed_content = content_result["content"]
js_processed_content = js_content_result["text"]
```

## Advanced Web Scraping with Playwright

The PlaywrightScraperTool provides advanced capabilities for scraping JavaScript-heavy websites:

```python
# Initialize the Playwright scraper tool
playwright_scraper = PlaywrightScraperTool()

# Basic usage
result = await playwright_scraper.run({
    "url": "https://example.com",
    "extract_type": "text",
})

# Advanced usage with JavaScript interaction
result = await playwright_scraper.run({
    "url": "https://example.com/login",
    "extract_type": "text",
    "js_scenario": [
        {"click": {"selector": "#login-button"}},
        {"fill": {"selector": "#username", "value": "testuser"}},
        {"fill": {"selector": "#password", "value": "password123"}},
        {"click": {"selector": "#submit-button"}},
        {"wait_for_navigation": {"timeout": 2000}},
    ],
})

# Handling infinite scroll pages
result = await playwright_scraper.run({
    "url": "https://example.com/feed",
    "extract_type": "text",
    "selector": ".post",
    "scroll_to_bottom": True,
})
```

## Model Context Protocol (MCP) Integration

The MCPTool provides a way to connect to MCP servers, which expose tools, resources, and prompts through a standardized protocol:

```python
from agents_hub.tools.standard import MCPTool

# Create an MCP tool for filesystem access using stdio transport
filesystem_tool = MCPTool(
    server_name="filesystem",
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-filesystem", "./"],
    transport="stdio",
)

# Create an MCP tool for GitHub access using stdio transport
github_tool = MCPTool(
    server_name="github",
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-github"],
    server_env={"GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token"},
    transport="stdio",
)

# Create an MCP tool using SSE transport
sse_tool = MCPTool(
    server_name="custom-server",
    server_url="http://localhost:8050/sse",
    transport="sse",
)

# List available tools
tools_result = await filesystem_tool.run({"operation": "list_tools"})

# Call a tool
tool_result = await filesystem_tool.run({
    "operation": "call_tool",
    "tool_name": "list_directory",
    "tool_arguments": {"path": "./"},
})

# Read a resource
resource_result = await filesystem_tool.run({
    "operation": "read_resource",
    "resource_path": "file://./README.md",
})

# Create an agent with MCP tools
agent = Agent(
    name="mcp_agent",
    llm=llm,
    tools=[filesystem_tool, github_tool],
    system_prompt="You are an assistant that can access files and GitHub repositories."
)
```
