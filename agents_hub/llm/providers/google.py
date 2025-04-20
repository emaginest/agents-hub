"""
Google Gemini LLM provider for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import json
import google.generativeai as genai
from agents_hub.llm.base import BaseLLM, LLMResponse
from agents_hub.tools.base import BaseTool


class GeminiProvider(BaseLLM):
    """
    Google Gemini LLM provider.

    This class implements the BaseLLM interface for Google Gemini models.
    """

    def __init__(self, api_key: str, model: str = "gemini-pro", **kwargs):
        """
        Initialize the Gemini provider.

        Args:
            api_key: Google API key
            model: Model to use for generation
            **kwargs: Additional parameters to pass to the Gemini client
        """
        self._model = model
        genai.configure(api_key=api_key)
        self._client = genai.GenerativeModel(model_name=model, **kwargs)

    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[BaseTool]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate a response from the Gemini model.

        Args:
            messages: List of messages in the conversation
            tools: Optional list of tools available to the model
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters to pass to the API

        Returns:
            LLMResponse object containing the generated text and any tool calls
        """
        # Convert messages to Gemini format
        gemini_messages = []
        for message in messages:
            role = message["role"]
            content = message["content"]

            # Map roles to Gemini format
            if role == "system":
                gemini_messages.append({"role": "user", "parts": [content]})
                gemini_messages.append(
                    {
                        "role": "model",
                        "parts": ["I'll follow these instructions carefully."],
                    }
                )
            elif role == "user":
                gemini_messages.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [content]})
            elif role == "tool":
                # Gemini doesn't have a direct equivalent for tool responses
                # We'll format it as a user message with clear labeling
                gemini_messages.append(
                    {"role": "user", "parts": [f"TOOL RESPONSE: {content}"]}
                )

        # Prepare function declarations if tools are provided
        function_declarations = None
        if tools:
            function_declarations = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
                for tool in tools
            ]

        # Make the API call
        chat = self._client.start_chat(history=gemini_messages[:-1])
        response = await chat.send_message_async(
            gemini_messages[-1]["parts"][0],
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
                "function_calling_config": (
                    {"functions": function_declarations}
                    if function_declarations
                    else None
                ),
            },
            **kwargs,
        )

        # Extract the response content
        content = response.text

        # Process function calls if any
        tool_calls = None
        if hasattr(response, "function_calls") and response.function_calls:
            tool_calls = []
            for function_call in response.function_calls:
                # Parse the arguments from JSON string to dict
                try:
                    arguments = json.loads(function_call.args)
                except json.JSONDecodeError:
                    arguments = function_call.args

                tool_calls.append(
                    {
                        "id": f"call_{len(tool_calls)}",
                        "name": function_call.name,
                        "arguments": arguments,
                    }
                )

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            raw_response=(
                response.candidates[0].model_dump()
                if hasattr(response, "candidates")
                else None
            ),
        )

    async def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding for the given text using Google's embedding model.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding
        """
        embedding = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_query",
        )
        return embedding["embedding"]

    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in the given text.

        This is an approximation as Gemini doesn't provide a direct way to count tokens.

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
        return "Google"

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
