"""
Tests for the MCP tool.
"""

import asyncio
import json
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agents_hub.tools.standard import MCPTool


# Mock MCP types and classes
class MockPromptMessage:
    def __init__(self, role, content):
        self.role = role
        self.content = content


class MockTextContent:
    def __init__(self, text):
        self.type = "text"
        self.text = text


class MockPrompt:
    def __init__(self, name, description, arguments=None):
        self.name = name
        self.description = description
        self.arguments = arguments or []


class MockPromptArgument:
    def __init__(self, name, description, required=False):
        self.name = name
        self.description = description
        self.required = required


class MockResource:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class MockTool:
    def __init__(self, name, description, input_schema=None):
        self.name = name
        self.description = description
        self.inputSchema = input_schema or {}


class MockListToolsResult:
    def __init__(self, tools):
        self.tools = tools


class MockListResourcesResult:
    def __init__(self, resources):
        self.resources = resources


class MockListPromptsResult:
    def __init__(self, prompts):
        self.prompts = prompts


class MockGetPromptResult:
    def __init__(self, description, messages):
        self.description = description
        self.messages = messages


class MockCallToolResult:
    def __init__(self, content):
        self.content = content


@pytest.fixture
def mock_session():
    """Create a mock MCP session."""
    session = AsyncMock()
    
    # Mock list_tools
    session.list_tools.return_value = MockListToolsResult([
        MockTool("test_tool", "A test tool", {"type": "object"}),
        MockTool("another_tool", "Another test tool", {"type": "object"}),
    ])
    
    # Mock list_resources
    session.list_resources.return_value = MockListResourcesResult([
        MockResource("test_resource", "A test resource"),
        MockResource("another_resource", "Another test resource"),
    ])
    
    # Mock list_prompts
    session.list_prompts.return_value = MockListPromptsResult([
        MockPrompt("test_prompt", "A test prompt", [
            MockPromptArgument("arg1", "Argument 1", True),
        ]),
    ])
    
    # Mock get_prompt
    session.get_prompt.return_value = MockGetPromptResult(
        "Test prompt description",
        [
            MockPromptMessage("user", MockTextContent("This is a test prompt")),
        ],
    )
    
    # Mock call_tool
    session.call_tool.return_value = MockCallToolResult([
        MockTextContent("Tool result"),
    ])
    
    # Mock read_resource
    session.read_resource.return_value = ("Resource content", "text/plain")
    
    return session


@pytest.fixture
def mock_stdio_client():
    """Create a mock stdio client."""
    async def mock_client(server_params):
        read_stream = AsyncMock()
        write_stream = AsyncMock()
        return (read_stream, write_stream)
    
    return mock_client


@pytest.fixture
def mock_sse_client():
    """Create a mock SSE client."""
    async def mock_client(url):
        read_stream = AsyncMock()
        write_stream = AsyncMock()
        return (read_stream, write_stream)
    
    return mock_client


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.stdio_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_initialization_stdio(mock_client_session, mock_stdio, mock_stdio_client):
    """Test MCPTool initialization with stdio transport."""
    # Set up mocks
    mock_stdio.return_value = mock_stdio_client
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_command="echo",
        server_args=["hello"],
        transport="stdio",
    )
    
    # Check initialization
    assert tool.server_name == "test"
    assert tool.transport == "stdio"
    assert tool.server_command == "echo"
    assert tool.server_args == ["hello"]
    assert tool.name == "mcp_test"


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.sse_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_initialization_sse(mock_client_session, mock_sse, mock_sse_client):
    """Test MCPTool initialization with SSE transport."""
    # Set up mocks
    mock_sse.return_value = mock_sse_client
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_url="http://localhost:8050/sse",
        transport="sse",
    )
    
    # Check initialization
    assert tool.server_name == "test"
    assert tool.transport == "sse"
    assert tool.server_url == "http://localhost:8050/sse"
    assert tool.name == "mcp_test"


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.stdio_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_list_tools(mock_client_session, mock_stdio, mock_stdio_client, mock_session):
    """Test MCPTool list_tools operation."""
    # Set up mocks
    mock_stdio.return_value = mock_stdio_client
    mock_client_session.return_value = mock_session
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_command="echo",
        server_args=["hello"],
        transport="stdio",
    )
    
    # Run the tool
    result = await tool.run({"operation": "list_tools"})
    
    # Check the result
    assert "tools" in result
    assert len(result["tools"]) == 2
    assert result["tools"][0]["name"] == "test_tool"
    assert result["tools"][1]["name"] == "another_tool"


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.stdio_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_list_resources(mock_client_session, mock_stdio, mock_stdio_client, mock_session):
    """Test MCPTool list_resources operation."""
    # Set up mocks
    mock_stdio.return_value = mock_stdio_client
    mock_client_session.return_value = mock_session
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_command="echo",
        server_args=["hello"],
        transport="stdio",
    )
    
    # Run the tool
    result = await tool.run({"operation": "list_resources"})
    
    # Check the result
    assert "resources" in result
    assert len(result["resources"]) == 2
    assert result["resources"][0]["name"] == "test_resource"
    assert result["resources"][1]["name"] == "another_resource"


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.stdio_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_read_resource(mock_client_session, mock_stdio, mock_stdio_client, mock_session):
    """Test MCPTool read_resource operation."""
    # Set up mocks
    mock_stdio.return_value = mock_stdio_client
    mock_client_session.return_value = mock_session
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_command="echo",
        server_args=["hello"],
        transport="stdio",
    )
    
    # Run the tool
    result = await tool.run({
        "operation": "read_resource",
        "resource_path": "test://resource",
    })
    
    # Check the result
    assert "content" in result
    assert result["content"] == "Resource content"
    assert result["mime_type"] == "text/plain"


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.stdio_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_call_tool(mock_client_session, mock_stdio, mock_stdio_client, mock_session):
    """Test MCPTool call_tool operation."""
    # Set up mocks
    mock_stdio.return_value = mock_stdio_client
    mock_client_session.return_value = mock_session
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_command="echo",
        server_args=["hello"],
        transport="stdio",
    )
    
    # Run the tool
    result = await tool.run({
        "operation": "call_tool",
        "tool_name": "test_tool",
        "tool_arguments": {"arg1": "value1"},
    })
    
    # Check the result
    assert "result" in result
    assert result["result"] == "Tool result"


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.stdio_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_list_prompts(mock_client_session, mock_stdio, mock_stdio_client, mock_session):
    """Test MCPTool list_prompts operation."""
    # Set up mocks
    mock_stdio.return_value = mock_stdio_client
    mock_client_session.return_value = mock_session
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_command="echo",
        server_args=["hello"],
        transport="stdio",
    )
    
    # Run the tool
    result = await tool.run({"operation": "list_prompts"})
    
    # Check the result
    assert "prompts" in result
    assert len(result["prompts"]) == 1
    assert result["prompts"][0]["name"] == "test_prompt"
    assert len(result["prompts"][0]["arguments"]) == 1
    assert result["prompts"][0]["arguments"][0]["name"] == "arg1"


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.stdio_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_get_prompt(mock_client_session, mock_stdio, mock_stdio_client, mock_session):
    """Test MCPTool get_prompt operation."""
    # Set up mocks
    mock_stdio.return_value = mock_stdio_client
    mock_client_session.return_value = mock_session
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_command="echo",
        server_args=["hello"],
        transport="stdio",
    )
    
    # Run the tool
    result = await tool.run({
        "operation": "get_prompt",
        "prompt_name": "test_prompt",
        "prompt_arguments": {"arg1": "value1"},
    })
    
    # Check the result
    assert "description" in result
    assert result["description"] == "Test prompt description"
    assert "messages" in result
    assert len(result["messages"]) == 1
    assert result["messages"][0]["role"] == "user"


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.stdio_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_invalid_operation(mock_client_session, mock_stdio, mock_stdio_client, mock_session):
    """Test MCPTool with an invalid operation."""
    # Set up mocks
    mock_stdio.return_value = mock_stdio_client
    mock_client_session.return_value = mock_session
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_command="echo",
        server_args=["hello"],
        transport="stdio",
    )
    
    # Run the tool with an invalid operation
    result = await tool.run({"operation": "invalid_operation"})
    
    # Check the result
    assert "error" in result
    assert "Unknown operation" in result["error"]


@pytest.mark.asyncio
@patch("agents_hub.tools.standard.mcp_tool.stdio_client")
@patch("agents_hub.tools.standard.mcp_tool.ClientSession")
async def test_mcp_tool_missing_parameters(mock_client_session, mock_stdio, mock_stdio_client, mock_session):
    """Test MCPTool with missing parameters."""
    # Set up mocks
    mock_stdio.return_value = mock_stdio_client
    mock_client_session.return_value = mock_session
    
    # Create the tool
    tool = MCPTool(
        server_name="test",
        server_command="echo",
        server_args=["hello"],
        transport="stdio",
    )
    
    # Run the tool with missing parameters
    result = await tool.run({
        "operation": "call_tool",
        # Missing tool_name
    })
    
    # Check the result
    assert "error" in result
    assert "tool_name is required" in result["error"]
