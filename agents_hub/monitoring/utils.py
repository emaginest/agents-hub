"""
Utility functions for the monitoring system.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import json
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Try to import tiktoken for OpenAI token counting
try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logger.warning(
        "tiktoken is not installed. Token counting for OpenAI models will be approximate. "
        "Install tiktoken for accurate token counting: pip install tiktoken"
    )


def count_tokens(text: str, model: str) -> int:
    """
    Count the number of tokens in a text string for a specific model.

    Args:
        text: Text to count tokens for
        model: Model name to use for token counting

    Returns:
        Number of tokens
    """
    if not text:
        return 0

    # Use tiktoken for OpenAI models if available
    if TIKTOKEN_AVAILABLE and model.startswith(("gpt-", "text-davinci-")):
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception as e:
            logger.warning(f"Error using tiktoken for model {model}: {e}")

    # Fallback to approximate token counting
    # A rough approximation is 4 characters per token for English text
    return len(text) // 4


def count_tokens_for_messages(
    messages: List[Dict[str, Any]], model: str
) -> Dict[str, int]:
    """
    Count the number of tokens in a list of messages for a specific model.

    Args:
        messages: List of messages to count tokens for
        model: Model name to use for token counting

    Returns:
        Dictionary with token counts (input_tokens)
    """
    if not messages:
        return {"input_tokens": 0}

    # For OpenAI chat models with tiktoken
    if TIKTOKEN_AVAILABLE and model.startswith(("gpt-")):
        try:
            encoding = tiktoken.encoding_for_model(model)

            # From OpenAI's documentation:
            # Every message follows <|start|>{role/name}\n{content}<|end|>
            # If there's a name, the role is omitted
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # <|start|> and <|end|> tokens
                for key, value in message.items():
                    num_tokens += len(encoding.encode(str(value)))
                    if key == "name":  # If there's a name, the role is omitted
                        num_tokens -= 1  # Role is omitted

            num_tokens += 2  # Every reply is primed with <|start|>assistant<|message|>

            return {"input_tokens": num_tokens}
        except Exception as e:
            logger.warning(f"Error using tiktoken for model {model}: {e}")

    # Fallback to approximate token counting
    total_tokens = 0
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, str):
            total_tokens += count_tokens(content, model)

    return {"input_tokens": total_tokens}


def get_model_pricing(model: str, provider: str) -> Tuple[float, float]:
    """
    Get the pricing information for a specific model and provider.

    Args:
        model: Model name
        provider: Provider name

    Returns:
        Tuple of (input_price_per_1k_tokens, output_price_per_1k_tokens)
    """
    # OpenAI pricing (as of April 2025)
    openai_pricing = {
        "gpt-4o": (5.0, 15.0),  # $5.00 per 1M input tokens, $15.00 per 1M output tokens
        "gpt-4o-mini": (
            0.15,
            0.60,
        ),  # $0.15 per 1M input tokens, $0.60 per 1M output tokens
        "gpt-4": (
            30.0,
            60.0,
        ),  # $30.00 per 1M input tokens, $60.00 per 1M output tokens
        "gpt-4-turbo": (
            10.0,
            30.0,
        ),  # $10.00 per 1M input tokens, $30.00 per 1M output tokens
        "gpt-3.5-turbo": (
            0.5,
            1.5,
        ),  # $0.50 per 1M input tokens, $1.50 per 1M output tokens
    }

    # Claude pricing (as of April 2025)
    claude_pricing = {
        "claude-3-opus-20240229": (
            15.0,
            75.0,
        ),  # $15.00 per 1M input tokens, $75.00 per 1M output tokens
        "claude-3-sonnet-20240229": (
            3.0,
            15.0,
        ),  # $3.00 per 1M input tokens, $15.00 per 1M output tokens
        "claude-3-haiku-20240307": (
            0.25,
            1.25,
        ),  # $0.25 per 1M input tokens, $1.25 per 1M output tokens
    }

    # Gemini pricing (as of April 2025)
    gemini_pricing = {
        "gemini-1.5-pro": (
            7.0,
            21.0,
        ),  # $7.00 per 1M input tokens, $21.00 per 1M output tokens
        "gemini-1.5-flash": (
            0.35,
            1.05,
        ),  # $0.35 per 1M input tokens, $1.05 per 1M output tokens
    }

    # Default pricing if model not found
    default_pricing = (
        10.0,
        30.0,
    )  # $10.00 per 1M input tokens, $30.00 per 1M output tokens

    # Get pricing based on provider and model
    if provider.lower() == "openai" or provider.lower() == "openaiprovider":
        # Try exact match first
        if model in openai_pricing:
            return openai_pricing[model]

        # Try prefix match
        for model_prefix, pricing in openai_pricing.items():
            if model.startswith(model_prefix):
                return pricing

        # Handle specific model variants
        if "gpt-4o" in model.lower():
            return openai_pricing["gpt-4o"]
        elif "gpt-4" in model.lower():
            return openai_pricing["gpt-4"]
        elif "gpt-3.5" in model.lower():
            return openai_pricing["gpt-3.5-turbo"]

    elif provider.lower() in ["anthropic", "claude", "claudeprovider"]:
        # Try exact match first
        if model in claude_pricing:
            return claude_pricing[model]

        # Try prefix match
        for model_prefix, pricing in claude_pricing.items():
            if model.startswith(model_prefix):
                return pricing

        # Handle specific model variants
        if "opus" in model.lower():
            return claude_pricing["claude-3-opus-20240229"]
        elif "sonnet" in model.lower():
            return claude_pricing["claude-3-sonnet-20240229"]
        elif "haiku" in model.lower():
            return claude_pricing["claude-3-haiku-20240307"]

    elif provider.lower() in ["google", "gemini", "geminiprovider"]:
        # Try exact match first
        if model in gemini_pricing:
            return gemini_pricing[model]

        # Try prefix match
        for model_prefix, pricing in gemini_pricing.items():
            if model.startswith(model_prefix):
                return pricing

        # Handle specific model variants
        if "pro" in model.lower():
            return gemini_pricing["gemini-1.5-pro"]
        elif "flash" in model.lower():
            return gemini_pricing["gemini-1.5-flash"]

    # Return default pricing if no match found
    logger.warning(
        f"No pricing information found for {provider}/{model}. Using default pricing."
    )
    return default_pricing


def estimate_cost(
    provider: str, model: str, input_tokens: int, output_tokens: int
) -> float:
    """
    Estimate the cost of an LLM call based on token usage.

    Args:
        provider: Provider name
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Estimated cost in USD
    """
    # Get pricing information
    input_price_per_1m, output_price_per_1m = get_model_pricing(model, provider)

    # Convert to price per token
    input_price_per_token = input_price_per_1m / 1_000_000
    output_price_per_token = output_price_per_1m / 1_000_000

    # Calculate cost
    input_cost = input_tokens * input_price_per_token
    output_cost = output_tokens * output_price_per_token
    total_cost = input_cost + output_cost

    return total_cost
