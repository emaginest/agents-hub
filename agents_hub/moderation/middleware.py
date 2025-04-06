"""
Moderation middleware for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Literal
import logging
from agents_hub.moderation.base import BaseContentModerator, ModerationResult


# Initialize logger
logger = logging.getLogger(__name__)


class ModerationMiddleware:
    """
    Middleware for content moderation in agents.
    
    This class provides middleware functions for pre-processing inputs and post-processing outputs.
    """
    
    def __init__(
        self,
        moderator: BaseContentModerator,
        on_input_violation: Literal["block", "warn", "log"] = "block",
        on_output_violation: Literal["block", "warn", "log"] = "block",
        input_violation_message: str = "I'm sorry, but I cannot respond to that request as it may violate content policies.",
        output_violation_message: str = "I apologize, but I cannot provide that response as it may violate content policies.",
        input_callback: Optional[Callable[[ModerationResult], Awaitable[None]]] = None,
        output_callback: Optional[Callable[[ModerationResult], Awaitable[None]]] = None,
    ):
        """
        Initialize the moderation middleware.
        
        Args:
            moderator: Content moderator to use
            on_input_violation: Action to take on input violation
            on_output_violation: Action to take on output violation
            input_violation_message: Message to return on input violation
            output_violation_message: Message to return on output violation
            input_callback: Optional callback for input violations
            output_callback: Optional callback for output violations
        """
        self.moderator = moderator
        self.on_input_violation = on_input_violation
        self.on_output_violation = on_output_violation
        self.input_violation_message = input_violation_message
        self.output_violation_message = output_violation_message
        self.input_callback = input_callback
        self.output_callback = output_callback
    
    async def process_input(self, text: str) -> Union[str, None]:
        """
        Process input text through moderation.
        
        Args:
            text: Input text to moderate
            
        Returns:
            Original text if safe, violation message if blocked, or None if warning
        """
        # Moderate the input
        result = await self.moderator.moderate(text)
        
        # Handle violation if flagged
        if result.flagged:
            # Call callback if provided
            if self.input_callback:
                await self.input_callback(result)
            
            # Handle based on violation action
            if self.on_input_violation == "block":
                logger.warning(f"Input blocked by moderation: {text}")
                return self.input_violation_message
            elif self.on_input_violation == "warn":
                logger.warning(f"Input flagged by moderation: {text}")
                return None
            else:  # "log"
                logger.warning(f"Input logged by moderation: {text}")
        
        # Return original text if not blocked
        return text
    
    async def process_output(self, text: str) -> str:
        """
        Process output text through moderation.
        
        Args:
            text: Output text to moderate
            
        Returns:
            Original text if safe, or violation message if blocked
        """
        # Moderate the output
        result = await self.moderator.moderate(text)
        
        # Handle violation if flagged
        if result.flagged:
            # Call callback if provided
            if self.output_callback:
                await self.output_callback(result)
            
            # Handle based on violation action
            if self.on_output_violation == "block":
                logger.warning(f"Output blocked by moderation: {text}")
                return self.output_violation_message
            elif self.on_output_violation == "warn":
                logger.warning(f"Output flagged by moderation: {text}")
            else:  # "log"
                logger.warning(f"Output logged by moderation: {text}")
        
        # Return original text if not blocked
        return text
