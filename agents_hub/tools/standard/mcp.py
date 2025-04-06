"""
MCP (Model Context Protocol) tool for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union, Literal
import logging
import json
from agents_hub.tools.base import BaseTool
from agents_hub.utils.mcp import MCPClient, MCPServerConfig, MCPTransport

# Initialize logger
logger = logging.getLogger(__name__)


class MCPTool(BaseTool):
    """Tool for connecting to Model Context Protocol servers."""
    
    def __init__(
        self,
        server_name: str,
        server_command: Optional[str] = None,
        server_args: Optional[List[str]] = None,
        server_env: Optional[Dict[str, str]] = None,
        transport: Literal["stdio", "sse", "websocket"] = "stdio",
        base_url: Optional[str] = None,
    ):
        """
        Initialize the MCP tool.
        
        Args:
            server_name: Name of the MCP server
            server_command: Command to start the server (for stdio transport)
            server_args: Arguments for the server command (for stdio transport)
            server_env: Environment variables for the server (for stdio transport)
            transport: Transport protocol to use
            base_url: Base URL for SSE or WebSocket transport
        """
        super().__init__(
            name=f"mcp_{server_name}",
            description=f"Connect to the {server_name} MCP server to access resources, tools, and prompts",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["list_resources", "read_resource", "list_tools", "call_tool", "list_prompts", "get_prompt"],
                        "description": "Operation to perform",
                    },
                    "resource_uri": {
                        "type": "string",
                        "description": "URI of the resource to read (for read_resource operation)",
                    },
                    "resource_params": {
                        "type": "object",
                        "description": "Parameters for the resource (for read_resource operation)",
                    },
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the tool to call (for call_tool operation)",
                    },
                    "tool_args": {
                        "type": "object",
                        "description": "Arguments for the tool (for call_tool operation)",
                    },
                    "prompt_name": {
                        "type": "string",
                        "description": "Name of the prompt to get (for get_prompt operation)",
                    },
                    "prompt_args": {
                        "type": "object",
                        "description": "Arguments for the prompt (for get_prompt operation)",
                    },
                },
                "required": ["operation"],
            },
        )
        
        # Create server configuration
        self.server_config = MCPServerConfig(
            name=server_name,
            transport=transport,
            command=server_command,
            args=server_args,
            env=server_env,
            base_url=base_url,
        )
        
        # Client will be created on demand
        self.client = None
    
    async def run(self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Run the MCP tool.
        
        Args:
            parameters: Parameters for the tool
            context: Optional context information
            
        Returns:
            Result of the operation
        """
        operation = parameters.get("operation")
        
        if not operation:
            return {"error": "Operation parameter is required"}
        
        try:
            # Create client if not already created
            if not self.client:
                self.client = MCPClient(self.server_config)
                await self.client.connect()
            
            # Perform the requested operation
            if operation == "list_resources":
                return await self._list_resources()
            
            elif operation == "read_resource":
                return await self._read_resource(parameters)
            
            elif operation == "list_tools":
                return await self._list_tools()
            
            elif operation == "call_tool":
                return await self._call_tool(parameters)
            
            elif operation == "list_prompts":
                return await self._list_prompts()
            
            elif operation == "get_prompt":
                return await self._get_prompt(parameters)
            
            else:
                return {"error": f"Unknown operation: {operation}"}
        
        except Exception as e:
            logger.exception(f"Error in MCP tool: {e}")
            return {"error": str(e)}
    
    async def _list_resources(self) -> Dict[str, Any]:
        """
        List available resources from the MCP server.
        
        Returns:
            Dictionary containing the list of resources
        """
        resources = await self.client.list_resources()
        
        return {
            "resources": [resource.model_dump() for resource in resources],
            "count": len(resources),
        }
    
    async def _read_resource(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read a resource from the MCP server.
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Resource content
        """
        resource_uri = parameters.get("resource_uri")
        if not resource_uri:
            return {"error": "resource_uri parameter is required for read_resource operation"}
        
        resource_params = parameters.get("resource_params")
        
        content = await self.client.read_resource(resource_uri, resource_params)
        
        return {
            "content": content,
            "uri": resource_uri,
        }
    
    async def _list_tools(self) -> Dict[str, Any]:
        """
        List available tools from the MCP server.
        
        Returns:
            Dictionary containing the list of tools
        """
        tools = await self.client.list_tools()
        
        return {
            "tools": [tool.model_dump() for tool in tools],
            "count": len(tools),
        }
    
    async def _call_tool(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Tool result
        """
        tool_name = parameters.get("tool_name")
        if not tool_name:
            return {"error": "tool_name parameter is required for call_tool operation"}
        
        tool_args = parameters.get("tool_args")
        
        result = await self.client.call_tool(tool_name, tool_args)
        
        return {
            "result": result,
            "tool": tool_name,
        }
    
    async def _list_prompts(self) -> Dict[str, Any]:
        """
        List available prompts from the MCP server.
        
        Returns:
            Dictionary containing the list of prompts
        """
        prompts = await self.client.list_prompts()
        
        return {
            "prompts": [prompt.model_dump() for prompt in prompts],
            "count": len(prompts),
        }
    
    async def _get_prompt(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get a prompt from the MCP server.
        
        Args:
            parameters: Tool parameters
            
        Returns:
            Prompt result
        """
        prompt_name = parameters.get("prompt_name")
        if not prompt_name:
            return {"error": "prompt_name parameter is required for get_prompt operation"}
        
        prompt_args = parameters.get("prompt_args")
        
        result = await self.client.get_prompt(prompt_name, prompt_args)
        
        return {
            "prompt": result.model_dump(),
            "name": prompt_name,
        }
