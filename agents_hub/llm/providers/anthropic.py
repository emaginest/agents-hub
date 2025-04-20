"""
Anthropic Claude LLM provider for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import json
import httpx
from anthropic import AsyncAnthropic
from agents_hub.llm.base import BaseLLM, LLMResponse
from agents_hub.tools.base import BaseTool


class ClaudeProvider(BaseLLM):
    """
    Anthropic Claude LLM provider.

    This class implements the BaseLLM interface for Anthropic Claude models.
    """

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307", **kwargs):
        """
        Initialize the Claude provider.

        Args:
            api_key: Anthropic API key
            model: Model to use for generation
            **kwargs: Additional parameters to pass to the AsyncAnthropic client
        """
        self._model = model
        self._client = AsyncAnthropic(api_key=api_key, **kwargs)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[BaseTool]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate a response from the Claude model.

        Args:
            messages: List of messages in the conversation
            tools: Optional list of tools available to the model
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the API

        Returns:
            LLMResponse object containing the generated text and any tool calls
        """
        # Prepare tools for Claude format if provided
        claude_tools = None
        if tools:
            claude_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.parameters,
                }
                for tool in tools
            ]

        # Make the API call
        response = await self._client.messages.create(
            model=self._model,
            messages=messages,
            tools=claude_tools,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Extract the response content and tool calls
        content = response.content[0].text

        # Process tool calls if any
        tool_calls = None
        if response.tool_use:
            tool_calls = []
            for tool_use in response.tool_use:
                # Parse the arguments from JSON string to dict
                try:
                    arguments = json.loads(tool_use.input)
                except json.JSONDecodeError:
                    arguments = tool_use.input

                tool_calls.append(
                    {
                        "id": tool_use.id,
                        "name": tool_use.name,
                        "arguments": arguments,
                    }
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            raw_response=response.model_dump(),
        )

    async def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding for the given text.

        Note: Claude doesn't provide a native embedding API, so we use a third-party service.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        # Claude doesn't have a native embedding API, so we raise an error
        raise NotImplementedError("Claude doesn't provide a native embedding API")

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in the given text.

        This is an approximation as Claude doesn't provide a direct way to count tokens.

        Args:
            text: Text to count tokens for

        Returns:
            Approximate number of tokens
        """
        # Simple approximation: 1 token ≈ 4 characters for English text
        return len(text) // 4

    @property
    def provider_name(self) -> str:
        """
        Get the name of the LLM provider.

        Returns:
            Provider name
        """
        return "Anthropic"

    @property
    def model_name(self) -> str:
        """
        Get the name of the model being used.

        Returns:
            Model name
        """
        return self._model

    @property
    def model(self) -> str:
        """
        Get the name of the model being used.
        This property is used by the monitoring system.

        Returns:
            Model name
        """
        return self._model
