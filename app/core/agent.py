from typing import List, Dict, Any, Optional
from app.config import Settings
from app.core.memory import memory
from app.core.retrieval import retrieve_context
from app.tools.calculator import calculator
from app.core.constants import SYSTEM_PROMPT
from app.utils.date_utils import get_current_date_info
from app.utils.monitoring import (
    monitored_client,
    create_trace,
    end_trace,
    flush_monitoring,
)
import json
import re

settings = Settings()


class AriaAgent:
    """ReAct agent implementation for ARIA."""

    def __init__(self):
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_maternal_health",
                    "description": "ALWAYS use this tool first to search through your maternal health knowledge base before responding to any pregnancy or health-related questions. This ensures you provide accurate, evidence-based information. Example: When asked about morning sickness, search for 'morning sickness treatments and recommendations' to get current medical guidance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The maternal health topic or question to search for",
                            }
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Use this tool for any numerical calculations related to pregnancy. Examples: Calculate due date from last menstrual period, determine gestational age in weeks, compute BMI or recommended weight gain. ALWAYS use this tool when questions involve dates, measurements, or numbers.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The mathematical expression to evaluate",
                            }
                        },
                        "required": ["expression"],
                    },
                },
            },
        ]

        self.tool_mapping = {
            "search_maternal_health": self._use_rag_tool,
            "calculate": self._use_calculator_tool,
        }

    async def _use_rag_tool(
        self, query: str, trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use the RAG tool to retrieve relevant context."""
        try:
            context = await retrieve_context(query)
            return {"status": "success", "context": context}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _use_calculator_tool(
        self, expression: str, trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Use the calculator tool to perform calculations."""
        try:
            result = calculator.run({"expression": expression})
            return {"status": "success", "result": result["result"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def _execute_tool_calls(
        self, tool_calls: List[Dict], trace_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute a series of tool calls and return their results."""
        results = []
        for call in tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)

            print(f"🛠️ ARIA using tool: {name}")
            print(f"📥 Tool input: {json.dumps(args, indent=2)}")

            if name in self.tool_mapping:
                tool_fn = self.tool_mapping[name]
                if name == "search_maternal_health":
                    result = await tool_fn(args["query"], trace_id)
                else:  # calculate
                    result = await tool_fn(args["expression"], trace_id)

                print(f"📤 Tool output: {json.dumps(result, indent=2)}")
                results.append(
                    {
                        "tool_call_id": call.id,
                        "role": "tool",
                        "name": name,
                        "content": json.dumps(result),
                    }
                )

        return results

    async def process_message(
        self,
        patient_id: str,
        message: str,
        recent_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response using the ReAct pattern.

        Args:
            patient_id: Unique identifier for the patient
            message: The user's message
            recent_history: Optional list of recent interactions

        Returns:
            Dictionary containing the agent's response and any tools used
        """
        # Create trace for this conversation
        trace_id = create_trace(patient_id)

        # Build conversation history with current date
        current_date = get_current_date_info()
        system_message = f"{SYSTEM_PROMPT}\n\nCurrent Date: {current_date}\nAlways be aware of this date when discussing timelines, due dates, or any time-sensitive information."

        messages = [{"role": "system", "content": system_message}]

        if recent_history:
            for interaction in recent_history:
                messages.append({"role": "user", "content": interaction["message"]})
                messages.append(
                    {"role": "assistant", "content": interaction["response"]}
                )

        messages.append({"role": "user", "content": message})

        print(f"👤 Patient message: {message}")

        # Get response with potential tool calls
        response = await monitored_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=self.tools,
            tool_choice="required",
            temperature=0.7,
            metadata={
                "patient_id": patient_id,
                "has_history": bool(recent_history),
                "trace_id": trace_id,
            },
        )

        tools_used = []
        current_response = response.choices[0].message

        # Handle tool calls if any
        while current_response.tool_calls:
            # Execute tool calls
            tool_results = await self._execute_tool_calls(
                current_response.tool_calls, trace_id
            )
            tools_used.extend([result["name"] for result in tool_results])

            # Add assistant's response and tool results to messages
            messages.append(
                {
                    "role": "assistant",
                    "content": current_response.content,
                    "tool_calls": current_response.tool_calls,
                }
            )
            messages.extend(
                [
                    {
                        "role": "tool",
                        "tool_call_id": r["tool_call_id"],
                        "content": r["content"],
                    }
                    for r in tool_results
                ]
            )

            # Get next response
            response = await monitored_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,
                metadata={
                    "patient_id": patient_id,
                    "has_history": bool(recent_history),
                    "trace_id": trace_id,
                },
            )
            current_response = response.choices[0].message

        final_content = current_response.content
        print(f"🤖 ARIA response: {final_content}")

        # Save interaction to memory
        await memory.save_interaction(
            patient_id=patient_id,
            ask=message,
            answer=final_content,
        )

        # End trace and flush events
        end_trace(trace_id)
        flush_monitoring()

        return {"response": final_content, "tools_used": tools_used}

    async def reformulate_response(
        self,
        patient_id: str,
        original_response: str,
        reformulation_type: str,
        specific_focus: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reformulate a previous response based on the specified type and focus.

        Args:
            patient_id: Unique identifier for the patient
            original_response: The response to reformulate
            reformulation_type: Type of reformulation (elaborate, simplify, clarify)
            specific_focus: Optional specific aspect to focus on

        Returns:
            Dictionary containing the reformulated response and tools used
        """
        # Create trace for this reformulation
        trace_id = create_trace(patient_id)

        # Build reformulation prompt
        current_date = get_current_date_info()

        reformulation_prompts = {
            "elaborate": "Please provide more detailed information about this topic. Include additional relevant details and examples.",
            "simplify": "Please explain this information in simpler terms, making it easier to understand.",
            "clarify": "Please clarify this information, focusing on making it more precise and clear.",
        }

        focus_prompt = (
            f" Specifically focus on explaining: {specific_focus}"
            if specific_focus
            else ""
        )

        prompt_template = reformulation_prompts.get(
            reformulation_type, "Please provide more information about this topic."
        )

        system_message = f"{SYSTEM_PROMPT}\n\nCurrent Date: {current_date}"
        user_message = f"{prompt_template}{focus_prompt}\n\nOriginal response:\n{original_response}"

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        print(f"🔄 Reformulating response ({reformulation_type})")
        print(f"📝 Original response: {original_response}")

        # Get response with potential tool calls
        response = await monitored_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=self.tools,
            tool_choice="required",
            temperature=0.7,
            metadata={
                "patient_id": patient_id,
                "reformulation_type": reformulation_type,
                "specific_focus": specific_focus,
                "trace_id": trace_id,
            },
        )

        tools_used = []
        current_response = response.choices[0].message

        # Handle tool calls if any
        while current_response.tool_calls:
            # Execute tool calls
            tool_results = await self._execute_tool_calls(
                current_response.tool_calls, trace_id
            )
            tools_used.extend([result["name"] for result in tool_results])

            # Add assistant's response and tool results to messages
            messages.append(
                {
                    "role": "assistant",
                    "content": current_response.content,
                    "tool_calls": current_response.tool_calls,
                }
            )
            messages.extend(
                [
                    {
                        "role": "tool",
                        "tool_call_id": r["tool_call_id"],
                        "content": r["content"],
                    }
                    for r in tool_results
                ]
            )

            # Get next response
            response = await monitored_client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,
                metadata={
                    "patient_id": patient_id,
                    "reformulation_type": reformulation_type,
                    "specific_focus": specific_focus,
                    "trace_id": trace_id,
                },
            )
            current_response = response.choices[0].message

        final_content = current_response.content
        print(f"🤖 ARIA reformulated response: {final_content}")

        # Save interaction to memory
        await memory.save_interaction(
            patient_id=patient_id,
            ask=f"Request to {reformulation_type} previous response{focus_prompt}",
            answer=final_content,
        )

        # End trace and flush events
        end_trace(trace_id)
        flush_monitoring()

        return {"response": final_content, "tools_used": tools_used}


# Create a global instance
aria = AriaAgent()
