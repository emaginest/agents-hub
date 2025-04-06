"""
MCP (Model Context Protocol) type definitions for the Agents Hub framework.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class MCPTransport(str, Enum):
    """Transport protocol for MCP connections."""
    STDIO = "stdio"
    SSE = "sse"
    WEBSOCKET = "websocket"


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""
    name: str = Field(..., description="Name of the MCP server")
    transport: MCPTransport = Field(MCPTransport.STDIO, description="Transport protocol to use")
    
    # For stdio transport
    command: Optional[str] = Field(None, description="Command to start the server (for stdio transport)")
    args: Optional[List[str]] = Field(None, description="Arguments for the server command (for stdio transport)")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables for the server (for stdio transport)")
    
    # For SSE or WebSocket transport
    base_url: Optional[str] = Field(None, description="Base URL for SSE or WebSocket transport")
    
    class Config:
        use_enum_values = True


class MCPResource(BaseModel):
    """MCP resource information."""
    uri: str = Field(..., description="URI of the resource")
    description: Optional[str] = Field(None, description="Description of the resource")
    parameters: Optional[List[Dict[str, Any]]] = Field(None, description="Parameters for the resource")


class MCPTool(BaseModel):
    """MCP tool information."""
    name: str = Field(..., description="Name of the tool")
    description: Optional[str] = Field(None, description="Description of the tool")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Parameters schema for the tool")


class MCPPrompt(BaseModel):
    """MCP prompt information."""
    name: str = Field(..., description="Name of the prompt")
    description: Optional[str] = Field(None, description="Description of the prompt")
    arguments: Optional[List[Dict[str, Any]]] = Field(None, description="Arguments for the prompt")


class MCPPromptMessage(BaseModel):
    """MCP prompt message."""
    role: str = Field(..., description="Role of the message sender")
    content: Union[str, Dict[str, Any]] = Field(..., description="Content of the message")


class MCPPromptResult(BaseModel):
    """Result of getting an MCP prompt."""
    description: Optional[str] = Field(None, description="Description of the prompt")
    messages: List[MCPPromptMessage] = Field(..., description="Messages in the prompt")
