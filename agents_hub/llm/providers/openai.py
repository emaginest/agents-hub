"""
OpenAI LLM provider for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import json
import httpx
from openai import AsyncOpenAI
from agents_hub.llm.base import BaseLLM, LLMResponse
from agents_hub.tools.base import BaseTool


class OpenAIProvider(BaseLLM):
    """
    OpenAI LLM provider.

    This class implements the BaseLLM interface for OpenAI models.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        base_url: Optional[str] = None,
        embedding_model: str = "text-embedding-3-small",
        **kwargs
    ):
        """
        Initialize the OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model to use for generation
            base_url: Optional base URL for API requests
            embedding_model: Model to use for embeddings
            **kwargs: Additional parameters to pass to the AsyncOpenAI client
        """
        self._model = model
        self._embedding_model = embedding_model
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url, **kwargs)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[BaseTool]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the OpenAI model.

        Args:
            messages: List of messages in the conversation
            tools: Optional list of tools available to the model
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the API

        Returns:
            LLMResponse object containing the generated text and any tool calls
        """
        # Prepare tools for OpenAI format if provided
        openai_tools = None
        if tools:
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    }
                }
                for tool in tools
            ]

        # Make the API call
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            tools=openai_tools,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        # Extract the response content and tool calls
        message = response.choices[0].message
        content = message.content or ""

        # Process tool calls if any
        tool_calls = None
        if message.tool_calls:
            tool_calls = []
            for tool_call in message.tool_calls:
                # Parse the arguments from JSON string to dict
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = tool_call.function.arguments

                tool_calls.append({
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": json.dumps(arguments) if isinstance(arguments, dict) else arguments,
                    }
                })

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            raw_response=response.model_dump(),
        )

    async def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding for the given text using OpenAI's embedding model.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        response = await self._client.embeddings.create(
            model=self._embedding_model,
            input=text,
        )
        return response.data[0].embedding

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in the given text.

        This is an approximation as OpenAI doesn't provide a direct way to count tokens.

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
        return "OpenAI"

    @property
    def model_name(self) -> str:
        """
        Get the name of the model being used.

        Returns:
            Model name
        """
        return self._model
