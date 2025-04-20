"""
Ollama LLM provider for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import json
import httpx
from agents_hub.llm.base import BaseLLM, LLMResponse
from agents_hub.tools.base import BaseTool


class OllamaProvider(BaseLLM):
    """
    Ollama LLM provider.

    This class implements the BaseLLM interface for local Ollama models.
    """

    def __init__(
        self, model: str = "llama3", base_url: str = "http://localhost:11434", **kwargs
    ):
        """
        Initialize the Ollama provider.

        Args:
            model: Model to use for generation
            base_url: Base URL for Ollama API
            **kwargs: Additional parameters for Ollama
        """
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._additional_params = kwargs

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[BaseTool]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate a response from the Ollama model.

        Args:
            messages: List of messages in the conversation
            tools: Optional list of tools available to the model
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the API

        Returns:
            LLMResponse object containing the generated text and any tool calls
        """
        # Prepare the request payload
        payload = {
            "model": self._model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                **self._additional_params,
                **kwargs,
            },
            "stream": False,
        }

        # If tools are provided, add them to the system prompt
        if tools:
            # Find the system message or create one
            system_message = None
            for i, message in enumerate(payload["messages"]):
                if message["role"] == "system":
                    system_message = message
                    break

            if system_message is None:
                system_message = {"role": "system", "content": ""}
                payload["messages"].insert(0, system_message)

            # Add tools to the system prompt
            tools_description = "\n\nYou have access to the following tools:\n\n"
            for tool in tools:
                tools_description += f"- {tool.name}: {tool.description}\n"
                tools_description += (
                    f"  Parameters: {json.dumps(tool.parameters, indent=2)}\n\n"
                )

            tools_description += (
                "\nTo use a tool, respond with a JSON object in the following format:\n"
            )
            tools_description += (
                '{"tool": "tool_name", "parameters": {"param1": "value1", ...}}\n'
            )
            tools_description += (
                "\nOnly use tools when necessary, and respond directly otherwise."
            )

            system_message["content"] += tools_description

        # Make the API call
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/api/chat", json=payload, timeout=60.0
            )
            response.raise_for_status()
            result = response.json()

        # Extract the response content
        content = result["message"]["content"]

        # Check if the response contains a tool call (in JSON format)
        tool_calls = None
        if tools and content.strip().startswith("{") and content.strip().endswith("}"):
            try:
                tool_call_data = json.loads(content)
                if "tool" in tool_call_data and "parameters" in tool_call_data:
                    # Extract the tool call
                    tool_calls = [
                        {
                            "id": "call_0",
                            "name": tool_call_data["tool"],
                            "arguments": tool_call_data["parameters"],
                        }
                    ]
                    # Set content to empty as it's a tool call
                    content = ""
            except json.JSONDecodeError:
                # Not a valid JSON, so it's a regular response
                pass

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            raw_response=result,
        )

    async def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding for the given text using Ollama's embedding endpoint.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        payload = {
            "model": self._model,
            "prompt": text,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._base_url}/api/embeddings", json=payload, timeout=30.0
            )
            response.raise_for_status()
            result = response.json()

        return result["embedding"]

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in the given text.

        This is an approximation as Ollama doesn't provide a direct way to count tokens.

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
        return "Ollama"

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
