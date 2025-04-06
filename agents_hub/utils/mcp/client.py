"""
MCP (Model Context Protocol) client implementation for the Agents Hub framework.
"""

import os
import json
import asyncio
import logging
import subprocess
from typing import Dict, List, Optional, Any, Union, Tuple
import aiohttp
# Updated imports for MCP 1.6.0
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client
from agents_hub.utils.mcp.types import (
    MCPServerConfig,
    MCPTransport,
    MCPResource,
    MCPTool,
    MCPPrompt,
    MCPPromptResult,
)

# Initialize logger
logger = logging.getLogger(__name__)


class MCPClient:
    """
    Client for connecting to MCP servers.

    This class provides a high-level interface for connecting to MCP servers
    and accessing their resources, tools, and prompts.
    """

    def __init__(self, config: MCPServerConfig):
        """
        Initialize the MCP client.

        Args:
            config: Configuration for the MCP server
        """
        self.config = config
        self.session = None
        self.process = None

    async def __aenter__(self):
        """Enter the async context manager."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async context manager."""
        await self.disconnect()

    async def connect(self) -> None:
        """
        Connect to the MCP server.

        Raises:
            RuntimeError: If the connection fails
        """
        try:
            if self.config.transport == MCPTransport.STDIO:
                if not self.config.command:
                    raise ValueError("Command is required for stdio transport")

                # Start the server process
                cmd = [self.config.command]
                if self.config.args:
                    cmd.extend(self.config.args)

                env = os.environ.copy()
                if self.config.env:
                    env.update(self.config.env)

                self.process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                )

                # Create the session using stdio_client
                self.session = await stdio_client(
                    stdin=self.process.stdin,
                    stdout=self.process.stdout
                )
                await self.session.start()

            elif self.config.transport == MCPTransport.SSE:
                if not self.config.base_url:
                    raise ValueError("Base URL is required for SSE transport")

                # SSE transport is not directly supported in MCP 1.6.0
                # We would need to implement a custom solution
                raise NotImplementedError("SSE transport is not supported in this version")

            elif self.config.transport == MCPTransport.WEBSOCKET:
                if not self.config.base_url:
                    raise ValueError("Base URL is required for WebSocket transport")

                # WebSocket transport is not directly supported in MCP 1.6.0
                # We would need to implement a custom solution
                raise NotImplementedError("WebSocket transport is not supported in this version")

            else:
                raise ValueError(f"Unsupported transport: {self.config.transport}")

        except Exception as e:
            logger.exception(f"Failed to connect to MCP server {self.config.name}: {e}")

            # Clean up if connection failed
            if self.process:
                self.process.terminate()
                self.process = None

            if self.session:
                await self.session.close()
                self.session = None

            raise RuntimeError(f"Failed to connect to MCP server {self.config.name}: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                logger.warning(f"Error closing MCP session: {e}")
            finally:
                self.session = None

        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except Exception as e:
                logger.warning(f"Error terminating MCP server process: {e}")
            finally:
                self.process = None

    async def list_resources(self) -> List[MCPResource]:
        """
        List available resources from the MCP server.

        Returns:
            List of resources

        Raises:
            RuntimeError: If the operation fails
        """
        if not self.session:
            await self.connect()

        try:
            resources = await self.session.list_resources()

            return [
                MCPResource(
                    uri=resource.uri,
                    description=resource.description,
                    parameters=[param.model_dump() for param in resource.parameters] if resource.parameters else None,
                )
                for resource in resources
            ]

        except Exception as e:
            logger.exception(f"Failed to list resources from MCP server {self.config.name}: {e}")
            raise RuntimeError(f"Failed to list resources: {e}")

    async def read_resource(self, uri: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Read a resource from the MCP server.

        Args:
            uri: URI of the resource to read
            params: Optional parameters for the resource

        Returns:
            Resource content

        Raises:
            RuntimeError: If the operation fails
        """
        if not self.session:
            await self.connect()

        try:
            content = await self.session.read_resource(uri, params)

            # Convert to dict if it's JSON
            if isinstance(content, str):
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return {"content": content}

            return content

        except Exception as e:
            logger.exception(f"Failed to read resource {uri} from MCP server {self.config.name}: {e}")
            raise RuntimeError(f"Failed to read resource {uri}: {e}")

    async def list_tools(self) -> List[MCPTool]:
        """
        List available tools from the MCP server.

        Returns:
            List of tools

        Raises:
            RuntimeError: If the operation fails
        """
        if not self.session:
            await self.connect()

        try:
            tools = await self.session.list_tools()

            return [
                MCPTool(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.parameters.model_dump() if tool.parameters else None,
                )
                for tool in tools
            ]

        except Exception as e:
            logger.exception(f"Failed to list tools from MCP server {self.config.name}: {e}")
            raise RuntimeError(f"Failed to list tools: {e}")

    async def call_tool(self, name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            name: Name of the tool to call
            args: Arguments for the tool

        Returns:
            Tool result

        Raises:
            RuntimeError: If the operation fails
        """
        if not self.session:
            await self.connect()

        try:
            result = await self.session.call_tool(name, args or {})

            # Convert to dict if it's JSON
            if isinstance(result, str):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"result": result}

            return result

        except Exception as e:
            logger.exception(f"Failed to call tool {name} on MCP server {self.config.name}: {e}")
            raise RuntimeError(f"Failed to call tool {name}: {e}")

    async def list_prompts(self) -> List[MCPPrompt]:
        """
        List available prompts from the MCP server.

        Returns:
            List of prompts

        Raises:
            RuntimeError: If the operation fails
        """
        if not self.session:
            await self.connect()

        try:
            prompts = await self.session.list_prompts()

            return [
                MCPPrompt(
                    name=prompt.name,
                    description=prompt.description,
                    arguments=[arg.model_dump() for arg in prompt.arguments] if prompt.arguments else None,
                )
                for prompt in prompts
            ]

        except Exception as e:
            logger.exception(f"Failed to list prompts from MCP server {self.config.name}: {e}")
            raise RuntimeError(f"Failed to list prompts: {e}")

    async def get_prompt(self, name: str, args: Optional[Dict[str, Any]] = None) -> MCPPromptResult:
        """
        Get a prompt from the MCP server.

        Args:
            name: Name of the prompt to get
            args: Arguments for the prompt

        Returns:
            Prompt result

        Raises:
            RuntimeError: If the operation fails
        """
        if not self.session:
            await self.connect()

        try:
            prompt = await self.session.get_prompt(name, args or {})

            return MCPPromptResult(
                description=prompt.description,
                messages=[
                    {
                        "role": message.role,
                        "content": message.content,
                    }
                    for message in prompt.messages
                ],
            )

        except Exception as e:
            logger.exception(f"Failed to get prompt {name} from MCP server {self.config.name}: {e}")
            raise RuntimeError(f"Failed to get prompt {name}: {e}")
