"""
Cognitive agent implementation for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Literal
import logging
import json
from pydantic import BaseModel, Field
from agents_hub.agents.base import Agent
from agents_hub.llm.base import BaseLLM
from agents_hub.memory.base import BaseMemory
from agents_hub.tools.base import BaseTool
from agents_hub.moderation.base import BaseContentModerator
from agents_hub.monitoring.base import BaseMonitor
from agents_hub.cognitive import CognitiveArchitecture
# No longer using the response formatter

# Initialize logger
logger = logging.getLogger(__name__)


class CognitiveAgentConfig(BaseModel):
    """Configuration for a cognitive agent."""
    reasoning_trace_enabled: bool = Field(True, description="Whether to include reasoning traces in responses")
    metacognition_enabled: bool = Field(True, description="Whether to enable metacognitive reflection")
    learning_enabled: bool = Field(True, description="Whether to enable learning from experience")
    reasoning_depth: int = Field(1, description="Depth of reasoning (1-3)")
    default_reasoning_mechanism: str = Field("deductive", description="Default reasoning mechanism")


class CognitiveAgent(Agent):
    """
    Agent with cognitive architecture capabilities.

    This class extends the base Agent class with a cognitive architecture
    that provides human-like cognitive capabilities.
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
        cognitive_architecture: Optional[CognitiveArchitecture] = None,
        cognitive_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the cognitive agent.

        Args:
            name: Name of the agent
            llm: LLM provider
            memory: Memory system
            tools: List of tools
            system_prompt: System prompt for the agent
            description: Description of the agent
            temperature: Temperature for LLM generation
            max_tokens: Maximum tokens for LLM generation
            moderation: Content moderator
            on_moderation_violation: Action to take on moderation violation
            monitor: Monitor for tracking agent interactions
            cognitive_architecture: Cognitive architecture configuration
            cognitive_config: Cognitive agent configuration
        """
        super().__init__(
            name=name,
            llm=llm,
            memory=memory,
            tools=tools,
            system_prompt=system_prompt,
            description=description,
            temperature=temperature,
            max_tokens=max_tokens,
            moderation=moderation,
            on_moderation_violation=on_moderation_violation,
            monitor=monitor,
        )

        # Initialize cognitive architecture
        self.cognitive_architecture = cognitive_architecture or CognitiveArchitecture()

        # Initialize cognitive configuration
        cognitive_config = cognitive_config or {}
        self.cognitive_config = CognitiveAgentConfig(**cognitive_config)

    async def run(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Run the agent with cognitive processing.

        Args:
            input_text: Input text to process
            context: Context information

        Returns:
            Agent response
        """
        context = context or {}
        conversation_id = context.get("conversation_id", "default")

        # Add cognitive configuration to context
        context["reasoning_trace_enabled"] = self.cognitive_config.reasoning_trace_enabled
        context["metacognition_enabled"] = self.cognitive_config.metacognition_enabled
        context["learning_enabled"] = self.cognitive_config.learning_enabled
        context["reasoning_depth"] = self.cognitive_config.reasoning_depth
        context["reasoning_mechanism"] = context.get("reasoning_mechanism", self.cognitive_config.default_reasoning_mechanism)

        # Track user message if monitoring is enabled
        if self.config.monitoring_enabled and self.monitor:
            await self.monitor.track_user_message(
                message=input_text,
                conversation_id=conversation_id,
                agent_name=self.config.name,
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

        try:
            # Add input to context
            context["input"] = input_text

            # First, check if we need to use tools
            if self.tools:
                # Use the base Agent's run method to handle tools
                base_response = await super().run(input_text, context)

                # Process the base response through cognitive architecture
                cognitive_result = await self.cognitive_architecture.process(base_response, context)

                # Generate a direct response using the LLM
                direct_response = await self._generate_direct_response(input_text, cognitive_result)

                # Use the direct response
                response = direct_response
            else:
                # Process input directly through cognitive architecture
                cognitive_result = await self.cognitive_architecture.process(input_text, context)

                # Generate a direct response using the LLM
                direct_response = await self._generate_direct_response(input_text, cognitive_result)

                # Use the direct response
                response = direct_response

            # Add reasoning trace if enabled
            if self.cognitive_config.reasoning_trace_enabled and "reasoning_trace" in cognitive_result:
                reasoning_trace = cognitive_result["reasoning_trace"]
                if reasoning_trace and not reasoning_trace in response:
                    response = f"{response}\n\nReasoning:\n{reasoning_trace}"

            # Apply moderation to output if enabled
            if self.config.moderation_enabled and self.moderation_middleware:
                response = await self.moderation_middleware.process_output(response)

            # Store the conversation in memory if available
            if self.memory:
                await self.memory.add_interaction(
                    conversation_id=conversation_id,
                    user_message=input_text,
                    assistant_message=response,
                )

            # Track assistant message if monitoring is enabled
            if self.config.monitoring_enabled and self.monitor:
                await self.monitor.track_assistant_message(
                    message=response,
                    conversation_id=conversation_id,
                    agent_name=self.config.name,
                    metadata=context.get("metadata"),
                )

            return response

        except Exception as e:
            logger.exception(f"Error in cognitive processing: {e}")

            # Track error if monitoring is enabled
            if self.config.monitoring_enabled and self.monitor:
                await self.monitor.track_error(
                    error=str(e),
                    conversation_id=conversation_id,
                    agent_name=self.config.name,
                )

            # Return a fallback response
            return f"I encountered an error in my thinking process. Let me try a simpler approach: {str(e)}"

    async def _generate_direct_response(self, input_text: str, cognitive_result: Dict[str, Any]) -> str:
        """
        Generate a direct response using the LLM based on the cognitive result.

        Args:
            input_text: Original input text
            cognitive_result: Result from the cognitive architecture

        Returns:
            Direct response
        """
        # Extract reasoning and metacognition from cognitive result
        reasoning = cognitive_result.get("reasoning", {})
        metacognition = cognitive_result.get("metacognition", {})

        # Create a prompt for the LLM to generate a direct response
        prompt = f"""You are an intelligent assistant with advanced cognitive capabilities.

        USER QUESTION: {input_text}

        Based on the following reasoning and metacognition, provide a direct, clear answer to the question.
        Do NOT repeat the question in your answer. Focus on providing a helpful, accurate response.

        REASONING:
        {json.dumps(reasoning, indent=2)}

        METACOGNITION:
        {json.dumps(metacognition, indent=2)}

        Your response should be concise, accurate, and directly address the question.
        """

        # Generate a response using the LLM
        messages = [
            {"role": "system", "content": "You are an intelligent assistant with advanced cognitive capabilities."},
            {"role": "user", "content": prompt}
        ]

        response = await self.llm.generate(
            messages=messages,
            temperature=0.3,  # Lower temperature for more focused responses
            max_tokens=500,
        )

        return response.content

    async def _process_tool_calls(
        self,
        tool_calls: List[Dict[str, Any]],
        messages: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> str:
        """
        Process tool calls with cognitive awareness.

        Args:
            tool_calls: Tool calls from the LLM
            messages: Messages for the LLM
            context: Context information

        Returns:
            Final response after processing tool calls
        """
        # Use the base implementation for tool calls
        return await super()._process_tool_calls(tool_calls, messages, context)
