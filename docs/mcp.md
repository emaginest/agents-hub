# Model Context Protocol (MCP) in Agents Hub

The Model Context Protocol (MCP) is a standardized protocol for connecting language models to external resources, tools, and prompts. Agents Hub provides a seamless integration with MCP, allowing agents to access a wide range of capabilities through MCP servers.

## What is MCP?

MCP is an open protocol that enables language models to:

1. **Access Resources**: Read files, databases, APIs, and other external data sources
2. **Use Tools**: Execute functions, run code, and interact with external systems
3. **Leverage Prompts**: Access pre-defined prompts and templates

MCP servers implement this protocol and provide specific capabilities, such as filesystem access, GitHub integration, database access, and more.

## MCP Tool in Agents Hub

Agents Hub provides the `MCPTool` class, which allows agents to connect to any MCP server and access its capabilities. The tool supports different transport protocols (stdio, SSE, WebSocket) and can be configured to connect to local or remote MCP servers.

### Available Operations

The MCP tool supports the following operations:

- **list_resources**: List available resources from the MCP server
- **read_resource**: Read a specific resource from the MCP server
- **list_tools**: List available tools from the MCP server
- **call_tool**: Call a specific tool on the MCP server
- **list_prompts**: List available prompts from the MCP server
- **get_prompt**: Get a specific prompt from the MCP server

### Popular MCP Servers

Here are some popular MCP servers that you can use with Agents Hub:

1. **Filesystem Server**: Access files and directories
   - Package: `@modelcontextprotocol/server-filesystem`
   - [GitHub Repository](https://github.com/modelcontextprotocol/server-filesystem)

2. **GitHub Server**: Access GitHub repositories, issues, and pull requests
   - Package: `@modelcontextprotocol/server-github`
   - [GitHub Repository](https://github.com/modelcontextprotocol/server-github)

3. **Web Server**: Access web pages and APIs
   - Package: `@modelcontextprotocol/server-web`
   - [GitHub Repository](https://github.com/modelcontextprotocol/server-web)

4. **Database Server**: Access SQL databases
   - Package: `@modelcontextprotocol/server-database`
   - [GitHub Repository](https://github.com/modelcontextprotocol/server-database)

## Installation

To use MCP with Agents Hub, you need to install the MCP Python SDK and the required transport libraries:

```bash
pip install mcp websockets
```

You also need to install the MCP servers you want to use. Most MCP servers are distributed as npm packages and can be installed using npx:

```bash
# No installation required, npx will download and run the package
npx -y @modelcontextprotocol/server-filesystem ./
```

## Usage Examples

### Filesystem Access

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import MCPTool

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create MCP tool for filesystem access
filesystem_tool = MCPTool(
    server_name="filesystem",
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-filesystem", "./"],
    transport="stdio",
)

# Create agent with the MCP tool
agent = Agent(
    name="filesystem_agent",
    llm=llm,
    tools=[filesystem_tool],
    system_prompt="You are an assistant that can access the filesystem. Use the mcp_filesystem tool to list and read files.",
)

# Use the agent to access files
response = await agent.run("List all Python files in the current directory")
response = await agent.run("Read the README.md file and summarize it")
```

### GitHub Access

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import MCPTool

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create MCP tool for GitHub access
github_tool = MCPTool(
    server_name="github",
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-github"],
    server_env={"GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token"},
    transport="stdio",
)

# Create agent with the MCP tool
agent = Agent(
    name="github_agent",
    llm=llm,
    tools=[github_tool],
    system_prompt="You are an assistant that can access GitHub repositories. Use the mcp_github tool to access repositories, issues, and pull requests.",
)

# Use the agent to access GitHub
response = await agent.run("List open issues in the repository")
response = await agent.run("Get the latest commit message")
```

### Web Access

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import MCPTool

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create MCP tool for web access
web_tool = MCPTool(
    server_name="web",
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-web"],
    transport="stdio",
)

# Create agent with the MCP tool
agent = Agent(
    name="web_agent",
    llm=llm,
    tools=[web_tool],
    system_prompt="You are an assistant that can access web pages. Use the mcp_web tool to fetch and analyze web content.",
)

# Use the agent to access web pages
response = await agent.run("Get the latest news from https://news.ycombinator.com/")
response = await agent.run("Search for information about climate change")
```

## Advanced Configuration

### Using SSE Transport

```python
from agents_hub.tools.standard import MCPTool

# Create MCP tool with SSE transport
sse_tool = MCPTool(
    server_name="remote_server",
    base_url="https://example.com/mcp",
    transport="sse",
)
```

### Using WebSocket Transport

```python
from agents_hub.tools.standard import MCPTool

# Create MCP tool with WebSocket transport
websocket_tool = MCPTool(
    server_name="remote_server",
    base_url="wss://example.com/mcp",
    transport="websocket",
)
```

### Using Multiple MCP Servers

```python
from agents_hub import Agent
from agents_hub.llm.providers import OpenAIProvider
from agents_hub.tools.standard import MCPTool

# Create LLM provider
llm = OpenAIProvider(api_key="your-openai-api-key")

# Create MCP tools for different servers
filesystem_tool = MCPTool(
    server_name="filesystem",
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-filesystem", "./"],
    transport="stdio",
)

github_tool = MCPTool(
    server_name="github",
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-github"],
    server_env={"GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token"},
    transport="stdio",
)

# Create agent with multiple MCP tools
agent = Agent(
    name="multi_tool_agent",
    llm=llm,
    tools=[filesystem_tool, github_tool],
    system_prompt="You are an assistant that can access files and GitHub repositories.",
)
```

## Troubleshooting

### Common Issues

1. **MCP Server Not Found**: Make sure the MCP server package is installed or accessible via npx.
2. **Connection Errors**: Check that the transport configuration is correct and the server is running.
3. **Permission Issues**: Ensure the agent has the necessary permissions to access the resources.
4. **Timeout Errors**: Increase the timeout settings if operations take too long.

### Debugging

To debug MCP connections, you can enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Resources

- [MCP Website](https://modelcontextprotocol.io/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Server Registry](https://modelcontextprotocol.io/servers)
