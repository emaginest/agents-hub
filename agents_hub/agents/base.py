"""
Base Agent class for the Agents Hub framework.
"""

import json
from typing import Dict, List, Any, Optional, Literal
from pydantic import BaseModel, Field
from agents_hub.llm.base import BaseLLM
from agents_hub.memory.base import BaseMemory
from agents_hub.tools.base import BaseTool
from agents_hub.moderation.base import BaseContentModerator
from agents_hub.moderation.middleware import ModerationMiddleware
from agents_hub.monitoring.base import BaseMonitor


class AgentConfig(BaseModel):
    """Configuration for an agent."""

    name: str = Field(..., description="Unique name for the agent")
    description: str = Field(
        "", description="Description of the agent's purpose and capabilities"
    )
    system_prompt: str = Field("", description="System prompt for the agent")
    temperature: float = Field(0.7, description="Temperature for LLM generation")
    max_tokens: int = Field(1000, description="Maximum tokens for LLM generation")
    tools_enabled: bool = Field(
        True, description="Whether tools are enabled for this agent"
    )
    moderation_enabled: bool = Field(
        False, description="Whether content moderation is enabled"
    )
    on_moderation_violation: Literal["block", "warn", "log"] = Field(
        "block", description="Action to take on moderation violation"
    )
    monitoring_enabled: bool = Field(False, description="Whether monitoring is enabled")


class Agent:
    """
    Base Agent class for the Agents Hub framework.

    An agent is a wrapper around an LLM that can use tools and memory to perform tasks.
    """

    def __init__(
        self,
        name: str,
        llm: BaseLLM,
        memory: Optional[BaseMemory] = None,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: str = "",
        description: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        moderation: Optional[BaseContentModerator] = None,
        on_moderation_violation: Literal["block", "warn", "log"] = "block",
        monitor: Optional[BaseMonitor] = None,
    ):
        """
        Initialize an agent.

        Args:
            name: Unique name for the agent
            llm: LLM provider to use for this agent
            memory: Memory provider to use for this agent
            tools: List of tools available to this agent
            system_prompt: System prompt for the agent
            description: Description of the agent's purpose and capabilities
            temperature: Temperature for LLM generation
            max_tokens: Maximum tokens for LLM generation
        """
        self.config = AgentConfig(
            name=name,
            description=description,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            tools_enabled=tools is not None and len(tools) > 0,
            moderation_enabled=moderation is not None,
            on_moderation_violation=on_moderation_violation,
            monitoring_enabled=monitor is not None,
        )

        self.llm = llm
        self.memory = memory
        self.tools = tools or []
        self._tool_map = {tool.name: tool for tool in self.tools}

        # Set up moderation if provided
        self.moderation = moderation
        if moderation:
            self.moderation_middleware = ModerationMiddleware(
                moderator=moderation,
                on_input_violation=on_moderation_violation,
                on_output_violation=on_moderation_violation,
            )
        else:
            self.moderation_middleware = None

        # Set up monitoring if provided
        self.monitor = monitor

    async def run(
        self, input_text: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Run the agent on the given input text.

        Args:
            input_text: The input text to process
            context: Optional context information

        Returns:
            The agent's response
        """
        context = context or {}
        conversation_id = context.get("conversation_id", "default")

        # Start monitoring if enabled
        if self.config.monitoring_enabled and self.monitor:
            # Start a conversation trace with user_id
            await self.monitor.start_conversation(
                conversation_id=conversation_id,
                agent_name=self.config.name,
                user_id=context.get("user_id"),
                metadata=context.get("metadata"),
            )

            # Track the user message
            await self.monitor.track_user_message(
                message=input_text,
                conversation_id=conversation_id,
                agent_name=self.config.name,
                user_id=context.get("user_id"),
                metadata=context.get("metadata"),
            )

        # Apply moderation to input if enabled
        if self.config.moderation_enabled and self.moderation_middleware:
            moderated_input = await self.moderation_middleware.process_input(input_text)
            if moderated_input != input_text:
                # Input was blocked by moderation
                if self.config.monitoring_enabled and self.monitor:
                    await self.monitor.track_error(
                        error="Input blocked by moderation",
                        conversation_id=conversation_id,
                        agent_name=self.config.name,
                    )
                return moderated_input
            input_text = moderated_input

        # Get conversation history from memory if available
        history = []
        if self.memory:
            history = await self.memory.get_history(conversation_id)

        # Prepare messages for the LLM
        messages = self._prepare_messages(input_text, history)

        # Track LLM call if monitoring is enabled
        if self.config.monitoring_enabled and self.monitor:
            await self.monitor.track_llm_call(
                provider=self.llm.__class__.__name__,
                model=getattr(self.llm, "model", "unknown"),
                messages=messages,
                conversation_id=conversation_id,
                agent_name=self.config.name,
                user_id=context.get("user_id"),
                input_tokens=context.get("input_tokens"),
            )

        try:
            # Get response from LLM
            response = await self.llm.generate(
                messages=messages,
                tools=self.tools if self.config.tools_enabled else None,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )

            # Track LLM result if monitoring is enabled
            if self.config.monitoring_enabled and self.monitor:
                await self.monitor.track_llm_result(
                    provider=self.llm.__class__.__name__,
                    model=getattr(self.llm, "model", "unknown"),
                    result=response.model_dump(),
                    conversation_id=conversation_id,
                    agent_name=self.config.name,
                    user_id=context.get("user_id"),
                    input_tokens=context.get("input_tokens"),
                )

            # Process tool calls if any
            if response.tool_calls and self.config.tools_enabled:
                final_response = await self._process_tool_calls(
                    response.tool_calls, messages, context
                )
            else:
                final_response = response.content

            # Apply moderation to output if enabled
            if self.config.moderation_enabled and self.moderation_middleware:
                final_response = await self.moderation_middleware.process_output(
                    final_response
                )

        except Exception as e:
            # Track error if monitoring is enabled
            if self.config.monitoring_enabled and self.monitor:
                await self.monitor.track_error(
                    error=str(e),
                    conversation_id=conversation_id,
                    agent_name=self.config.name,
                    user_id=context.get("user_id"),
                )
            raise

        # Save to memory if available
        if self.memory:
            await self.memory.add_interaction(
                conversation_id=conversation_id,
                user_message=input_text,
                assistant_message=final_response,
            )

        # Track assistant message if monitoring is enabled
        if self.config.monitoring_enabled and self.monitor:
            await self.monitor.track_assistant_message(
                message=final_response,
                conversation_id=conversation_id,
                agent_name=self.config.name,
                user_id=context.get("user_id"),
                metadata=context.get("metadata"),
            )

        return final_response

    def _prepare_messages(
        self, input_text: str, history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Prepare messages for the LLM.

        Args:
            input_text: The input text to process
            history: Conversation history

        Returns:
            List of messages for the LLM
        """
        messages = []

        # Add system message if provided
        if self.config.system_prompt:
            messages.append({"role": "system", "content": self.config.system_prompt})

        # Add conversation history
        for entry in history:
            messages.append({"role": "user", "content": entry["user_message"]})
            messages.append(
                {"role": "assistant", "content": entry["assistant_message"]}
            )

        # Add current user message
        messages.append({"role": "user", "content": input_text})

        return messages

    async def _process_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        messages: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        """
        Process tool calls from the LLM.

        Args:
            tool_calls: List of tool calls from the LLM
            messages: Current message history
            context: Context information

        Returns:
            Final response after processing tool calls
        """
        conversation_id = context.get("conversation_id", "default")

        # Process each tool call
        for tool_call in tool_calls:
            # Ensure tool call has the required fields
            if "type" not in tool_call:
                tool_call["type"] = "function"

            # Create an assistant message with this tool call
            assistant_message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call],
            }

            # Add the assistant message with the tool call
            messages.append(assistant_message)

            # Get tool details
            tool_name = tool_call.get("function", {}).get("name")
            tool_args_str = tool_call.get("function", {}).get("arguments", "{}")

            # Parse tool arguments
            try:
                if isinstance(tool_args_str, str):
                    tool_args = json.loads(tool_args_str)
                else:
                    tool_args = tool_args_str
            except json.JSONDecodeError:
                tool_args = {"query": tool_args_str}  # Fallback for non-JSON strings

            # Get the tool
            tool = self._tool_map.get(tool_name)
            if not tool:
                tool_result = {"error": f"Tool '{tool_name}' not found"}

                # Track error if monitoring is enabled
                if self.config.monitoring_enabled and self.monitor:
                    await self.monitor.track_error(
                        error=f"Tool '{tool_name}' not found",
                        conversation_id=conversation_id,
                        agent_name=self.config.name,
                    )
            else:
                try:
                    # Track tool call if monitoring is enabled
                    if self.config.monitoring_enabled and self.monitor:
                        await self.monitor.track_tool_usage(
                            tool_name=tool_name,
                            input_data=tool_args,
                            output_data=None,  # Will be updated after tool execution
                            conversation_id=conversation_id,
                            agent_name=self.config.name,
                            user_id=context.get("user_id"),
                        )

                    # Run the tool
                    tool_result = await tool.run(tool_args, context)

                    # Track tool result if monitoring is enabled
                    if self.config.monitoring_enabled and self.monitor:
                        await self.monitor.track_tool_usage(
                            tool_name=tool_name,
                            input_data=tool_args,
                            output_data=tool_result,
                            conversation_id=conversation_id,
                            agent_name=self.config.name,
                            user_id=context.get("user_id"),
                        )
                except Exception as e:
                    error_message = f"Error running tool '{tool_name}': {str(e)}"
                    tool_result = {"error": error_message}

                    # Track error if monitoring is enabled
                    if self.config.monitoring_enabled and self.monitor:
                        await self.monitor.track_error(
                            error=error_message,
                            conversation_id=conversation_id,
                            agent_name=self.config.name,
                            user_id=context.get("user_id"),
                        )

            # Get the tool call ID
            tool_call_id = tool_call.get("id")
            if not tool_call_id:
                continue  # Skip if no ID

            # Add the tool result message immediately after the assistant message
            tool_result_str = (
                json.dumps(tool_result)
                if isinstance(tool_result, dict)
                else str(tool_result)
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_result_str,
                }
            )

        # Get final response from LLM
        final_response = await self.llm.generate(
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return final_response.content

    def add_tool(self, tool: BaseTool) -> None:
        """
        Add a tool to the agent.

        Args:
            tool: Tool to add
        """
        self.tools.append(tool)
        self._tool_map[tool.name] = tool
        self.config.tools_enabled = True

    def remove_tool(self, tool_name: str) -> None:
        """
        Remove a tool from the agent.

        Args:
            tool_name: Name of the tool to remove
        """
        if tool_name in self._tool_map:
            tool = self._tool_map[tool_name]
            self.tools.remove(tool)
            del self._tool_map[tool_name]
            self.config.tools_enabled = len(self.tools) > 0
