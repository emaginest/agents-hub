"""
MCP (Model Context Protocol) tool for the Agents Hub framework.

This module provides a tool for connecting to MCP servers using either SSE or stdio transport.
It allows agents to access resources, call tools, and use prompts provided by MCP servers.
"""

import json
import logging
import traceback
from typing import Any, Dict, List, Optional

from agents_hub.tools.base import BaseTool

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.client.sse import sse_client
except ImportError:
    raise ImportError(
        "The mcp package is required to use the MCPTool. "
        "Please install it with `pip install mcp[cli]`."
    )

# Initialize logger
logger = logging.getLogger(__name__)


class MCPTool(BaseTool):
    """
    Tool for connecting to MCP (Model Context Protocol) servers.

    This tool provides methods for connecting to MCP servers using either SSE or stdio transport.
    It allows agents to access resources, call tools, and use prompts provided by MCP servers.

    The tool can be used as an async context manager to ensure proper cleanup:

    ```python
    async with MCPTool(...) as tool:
        result = await tool.run(...)
    ```

    Example:
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

        # Use the tool
        result = await agent.run_tool("filesystem", {
            "operation": "list_resources",
        })
        ```
    """

    def __init__(
        self,
        server_name: str,
        transport: str = "stdio",
        server_command: Optional[str] = None,
        server_args: Optional[List[str]] = None,
        server_env: Optional[Dict[str, str]] = None,
        server_url: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Initialize the MCP tool.

        Args:
            server_name: Name of the MCP server
            transport: Transport mechanism to use ("stdio" or "sse")
            server_command: Command to run the MCP server (required for stdio transport)
            server_args: Arguments to pass to the server command (for stdio transport)
            server_env: Environment variables to set for the server (for stdio transport)
            server_url: URL of the MCP server (required for sse transport)
            timeout: Timeout in seconds for MCP operations
        """
        super().__init__(
            name=f"mcp_{server_name}",
            description=f"Connect to the {server_name} MCP server",
            parameters={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "list_tools",
                            "call_tool",
                            "list_resources",
                            "read_resource",
                            "list_prompts",
                            "get_prompt",
                        ],
                        "description": "Operation to perform",
                    },
                    "tool_name": {
                        "type": "string",
                        "description": "Name of the tool to call (for call_tool operation)",
                    },
                    "tool_arguments": {
                        "type": "object",
                        "description": "Arguments for the tool (for call_tool operation)",
                    },
                    "resource_path": {
                        "type": "string",
                        "description": "Path of the resource to read (for read_resource operation)",
                    },
                    "prompt_name": {
                        "type": "string",
                        "description": "Name of the prompt to get (for get_prompt operation)",
                    },
                    "prompt_arguments": {
                        "type": "object",
                        "description": "Arguments for the prompt (for get_prompt operation)",
                    },
                },
                "required": ["operation"],
            },
        )

        self.server_name = server_name
        self.transport = transport
        self.server_command = server_command
        self.server_args = server_args or []
        self.server_env = server_env or {}
        self.server_url = server_url
        self.timeout = timeout

        # Validate configuration
        if transport == "stdio" and not server_command:
            raise ValueError("server_command is required for stdio transport")
        if transport == "sse" and not server_url:
            raise ValueError("server_url is required for sse transport")

        # Session state
        self._session = None
        self._transport = None
        self._initialized = False
        self._transport_cm = None
        self._session_cm = None

    async def __aenter__(self):
        """Enter the async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        await self.close()
        return False  # Don't suppress exceptions

    async def _initialize_session(self) -> None:
        """Initialize the MCP session if not already initialized."""
        if self._initialized:
            return

        try:
            # Create transport
            if self.transport == "stdio":
                # Create server parameters for stdio connection
                server_params = StdioServerParameters(
                    command=self.server_command,
                    args=self.server_args,
                    env=self.server_env,
                )

                # Connect to the server via stdio
                self._transport_cm = stdio_client(server_params)
            else:  # sse
                # Connect to the server via SSE
                self._transport_cm = sse_client(self.server_url)

            # Enter the transport context manager
            read_stream, write_stream = await self._transport_cm.__aenter__()

            # Create and enter the session context manager
            self._session_cm = ClientSession(read_stream, write_stream)
            self._session = await self._session_cm.__aenter__()

            # Initialize the session
            await self._session.initialize()

            self._initialized = True
            logger.info(f"Connected to MCP server: {self.server_name}")
        except Exception as e:
            # Clean up if initialization fails
            logger.error(f"Error connecting to MCP server: {e}")
            await self._cleanup_resources()
            raise

    async def _cleanup_resources(self) -> None:
        """Clean up resources without raising exceptions."""
        # Clean up session
        if self._session_cm is not None:
            try:
                await self._session_cm.__aexit__(None, None, None)
            except Exception as e:
                logger.debug(f"Error closing session: {e}")
            finally:
                self._session = None
                self._session_cm = None

        # Clean up transport
        if self._transport_cm is not None:
            try:
                await self._transport_cm.__aexit__(None, None, None)
            except Exception as e:
                logger.debug(f"Error closing transport: {e}")
            finally:
                self._transport = None
                self._transport_cm = None

        self._initialized = False

    async def close(self) -> None:
        """Close the MCP tool and release all resources."""
        if not self._initialized:
            return

        try:
            logger.info(f"Closing MCP tool for {self.server_name}")
            await self._cleanup_resources()
            logger.info(f"Disconnected from MCP server: {self.server_name}")
        except Exception as e:
            logger.error(f"Error disconnecting from MCP server: {e}")
            # Still mark as not initialized even if there was an error
            self._initialized = False

    async def run(
        self, parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Run the MCP tool with the given parameters.

        Args:
            parameters: Parameters for the tool
            context: Optional context information from the agent

        Returns:
            Result of running the tool
        """
        operation = parameters.get("operation")
        if not operation:
            return {"error": "Operation is required"}

        try:
            # Initialize the session if not already initialized
            await self._initialize_session()

            # Perform the requested operation
            if operation == "list_tools":
                return await self._list_tools()
            elif operation == "call_tool":
                tool_name = parameters.get("tool_name")
                tool_arguments = parameters.get("tool_arguments", {})
                if not tool_name:
                    error_msg = "tool_name is required for call_tool operation"
                    logger.error(error_msg)
                    return {
                        "error": error_msg,
                        "status": "failed",
                        "operation": operation,
                    }
                return await self._call_tool(tool_name, tool_arguments)
            elif operation == "list_resources":
                return await self._list_resources()
            elif operation == "read_resource":
                resource_path = parameters.get("resource_path")
                if not resource_path:
                    error_msg = "resource_path is required for read_resource operation"
                    logger.error(error_msg)
                    return {
                        "error": error_msg,
                        "status": "failed",
                        "operation": operation,
                    }
                return await self._read_resource(resource_path)
            elif operation == "list_prompts":
                return await self._list_prompts()
            elif operation == "get_prompt":
                prompt_name = parameters.get("prompt_name")
                prompt_arguments = parameters.get("prompt_arguments", {})
                if not prompt_name:
                    error_msg = "prompt_name is required for get_prompt operation"
                    logger.error(error_msg)
                    return {
                        "error": error_msg,
                        "status": "failed",
                        "operation": operation,
                    }
                return await self._get_prompt(prompt_name, prompt_arguments)
            else:
                error_msg = f"Unknown operation: {operation}"
                logger.error(error_msg)
                return {"error": error_msg, "status": "failed", "operation": operation}
        except ConnectionError as e:
            error_msg = f"Connection error with MCP server: {e}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "status": "connection_error",
                "operation": operation,
            }
        except TimeoutError as e:
            error_msg = f"Timeout while communicating with MCP server: {e}"
            logger.error(error_msg)
            return {"error": error_msg, "status": "timeout", "operation": operation}
        except Exception as e:
            error_msg = f"Error in MCP tool: {e}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg, "status": "error", "operation": operation}

    async def _list_tools(self) -> Dict[str, Any]:
        """
        List available tools from the MCP server.

        Returns:
            Dictionary containing the list of tools
        """
        try:
            tools_result = await self._session.list_tools()
            return {
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    }
                    for tool in tools_result.tools
                ]
            }
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return {"error": str(e)}

    async def _call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Result of the tool call
        """
        try:
            result = await self._session.call_tool(tool_name, arguments=arguments)

            # Extract the result content
            if result.content and len(result.content) > 0:
                content = result.content[0].text
                try:
                    # Try to parse as JSON
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Return as text if not valid JSON
                    return {
                        "result": content,
                        "status": "success",
                        "tool_name": tool_name,
                        "format": "text",
                    }

            return {
                "result": "Tool executed successfully but returned no content",
                "status": "success",
                "tool_name": tool_name,
            }
        except ConnectionError as e:
            error_msg = f"Connection error calling tool {tool_name}: {e}"
            logger.error(error_msg)
            return {
                "error": error_msg,
                "status": "connection_error",
                "tool_name": tool_name,
            }
        except TimeoutError as e:
            error_msg = f"Timeout calling tool {tool_name}: {e}"
            logger.error(error_msg)
            return {"error": error_msg, "status": "timeout", "tool_name": tool_name}
        except Exception as e:
            error_msg = f"Error calling tool {tool_name}: {e}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            return {"error": error_msg, "status": "error", "tool_name": tool_name}

    async def _list_resources(self) -> Dict[str, Any]:
        """
        List available resources from the MCP server.

        Returns:
            Dictionary containing the list of resources
        """
        try:
            resources_result = await self._session.list_resources()
            return {
                "resources": [
                    {
                        "name": resource.name,
                        "description": resource.description,
                    }
                    for resource in resources_result.resources
                ]
            }
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return {"error": str(e)}

    async def _read_resource(self, resource_path: str) -> Dict[str, Any]:
        """
        Read a resource from the MCP server.

        Args:
            resource_path: Path of the resource to read

        Returns:
            Content of the resource
        """
        try:
            result = await self._session.read_resource(resource_path)

            # The result structure might vary depending on the MCP version
            # Try to extract content and mime_type in a robust way
            if hasattr(result, "contents") and result.contents:
                # New MCP format
                content_item = result.contents[0]
                content = (
                    content_item.text
                    if hasattr(content_item, "text")
                    else str(content_item)
                )
                mime_type = (
                    content_item.mimeType
                    if hasattr(content_item, "mimeType")
                    else "text/plain"
                )
            elif isinstance(result, tuple) and len(result) == 2:
                # Old MCP format (content, mime_type)
                content, mime_type = result

                # Handle tuple format with meta and contents
                if (
                    isinstance(content, str)
                    and content == "meta"
                    and isinstance(mime_type, tuple)
                ):
                    _, contents = mime_type  # Ignore the meta part
                    if contents and hasattr(contents[0], "text"):
                        content = contents[0].text
                        mime_type = (
                            contents[0].mimeType
                            if hasattr(contents[0], "mimeType")
                            else "text/plain"
                        )
            else:
                # Unknown format, just convert to string
                content = str(result)
                mime_type = "text/plain"

            # Handle different mime types
            if isinstance(mime_type, str) and mime_type.startswith("application/json"):
                try:
                    return {"content": json.loads(content), "mime_type": mime_type}
                except (json.JSONDecodeError, TypeError):
                    return {"content": str(content), "mime_type": mime_type}
            else:
                return {"content": str(content), "mime_type": str(mime_type)}
        except Exception as e:
            logger.error(f"Error reading resource {resource_path}: {e}")
            return {"error": str(e)}

    async def _list_prompts(self) -> Dict[str, Any]:
        """
        List available prompts from the MCP server.

        Returns:
            Dictionary containing the list of prompts
        """
        try:
            prompts_result = await self._session.list_prompts()
            return {
                "prompts": [
                    {
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": [
                            {
                                "name": arg.name,
                                "description": arg.description,
                                "required": arg.required,
                            }
                            for arg in prompt.arguments
                        ],
                    }
                    for prompt in prompts_result.prompts
                ]
            }
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return {"error": str(e)}

    async def _get_prompt(
        self, prompt_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get a prompt from the MCP server.

        Args:
            prompt_name: Name of the prompt to get
            arguments: Arguments for the prompt

        Returns:
            Prompt content
        """
        try:
            prompt_result = await self._session.get_prompt(
                prompt_name, arguments=arguments
            )

            # Extract messages
            messages = []
            for message in prompt_result.messages:
                if hasattr(message, "content") and hasattr(message.content, "text"):
                    messages.append(
                        {
                            "role": message.role,
                            "content": message.content.text,
                        }
                    )

            return {
                "description": prompt_result.description,
                "messages": messages,
            }
        except Exception as e:
            logger.error(f"Error getting prompt {prompt_name}: {e}")
            return {"error": str(e)}

    def __del__(self):
        """Clean up resources when the object is deleted."""
        # We can't use await in __del__, so we just log a message
        if hasattr(self, "_initialized") and self._initialized:
            logger.warning(
                f"MCPTool for {self.server_name} was not properly closed. "
                f"Use 'await tool.close()' or 'async with tool:' to properly clean up resources."
            )
