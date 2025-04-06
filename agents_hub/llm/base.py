"""
Base LLM interface for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """Response from an LLM."""
    content: str = Field("", description="The text content of the response")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="Tool calls requested by the LLM")
    raw_response: Optional[Dict[str, Any]] = Field(None, description="Raw response from the LLM provider")


class BaseLLM:
    """
    Base class for LLM providers.
    
    This abstract class defines the interface that all LLM providers must implement.
    """
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Any]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of messages in the conversation
            tools: Optional list of tools available to the LLM
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse object containing the generated text and any tool calls
        """
        raise NotImplementedError("Subclasses must implement generate()")
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Get an embedding for the given text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        raise NotImplementedError("Subclasses must implement get_embedding()")
    
    def get_token_count(self, text: str) -> int:
        """
        Get the number of tokens in the given text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        raise NotImplementedError("Subclasses must implement get_token_count()")
    
    @property
    def provider_name(self) -> str:
        """
        Get the name of the LLM provider.
        
        Returns:
            Provider name
        """
        raise NotImplementedError("Subclasses must implement provider_name()")
    
    @property
    def model_name(self) -> str:
        """
        Get the name of the model being used.
        
        Returns:
            Model name
        """
        raise NotImplementedError("Subclasses must implement model_name()")
