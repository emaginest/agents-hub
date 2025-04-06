"""
Patch for the Agent class to fix tool call handling.
"""

from typing import Dict, List, Any
import json


async def patched_process_tool_calls(
    self,
    tool_calls: List[Dict[str, Any]],
    messages: List[Dict[str, Any]],
    context: Dict[str, Any]
) -> str:
    """
    Process tool calls from the LLM with improved handling of tool call IDs.

    Args:
        tool_calls: List of tool calls from the LLM
        messages: Current message history
        context: Context information

    Returns:
        Final response after processing tool calls
    """
    conversation_id = context.get("conversation_id", "default")

    # Process each tool call
    for i, tool_call in enumerate(tool_calls):
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
                    )

        # Get the tool call ID
        tool_call_id = tool_call.get("id")
        if not tool_call_id:
            continue  # Skip if no ID

        # Add the tool result message immediately after the assistant message
        tool_result_str = json.dumps(tool_result) if isinstance(tool_result, dict) else str(tool_result)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": tool_result_str,
        })

    # Get final response from LLM
    final_response = await self.llm.generate(
        messages=messages,
        temperature=self.config.temperature,
        max_tokens=self.config.max_tokens,
    )

    return final_response.content
