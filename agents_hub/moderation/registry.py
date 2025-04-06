"""
Moderation registry for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union, Literal
import logging
from agents_hub.moderation.base import BaseContentModerator, ModerationResult, ModerationViolation, ModerationCategory


# Initialize logger
logger = logging.getLogger(__name__)


class ModerationRegistry(BaseContentModerator):
    """
    Moderation registry for managing multiple moderators.
    
    This class allows combining multiple moderators with different strategies.
    """
    
    def __init__(
        self,
        moderators: List[BaseContentModerator],
        mode: Literal["any", "all", "majority"] = "any",
    ):
        """
        Initialize the moderation registry.
        
        Args:
            moderators: List of moderators to use
            mode: Moderation mode:
                - "any": Flag if any moderator flags content
                - "all": Flag only if all moderators flag content
                - "majority": Flag if majority of moderators flag content
        """
        self.moderators = moderators
        self.mode = mode
    
    async def moderate(self, text: str) -> ModerationResult:
        """
        Moderate the given text using all registered moderators.
        
        Args:
            text: Text to moderate
            
        Returns:
            ModerationResult object containing the moderation decision
        """
        if not self.moderators:
            # No moderators, return safe result
            return ModerationResult(
                flagged=False,
                violations=[],
                original_text=text,
            )
        
        # Run all moderators
        results = []
        for moderator in self.moderators:
            try:
                result = await moderator.moderate(text)
                results.append(result)
            except Exception as e:
                logger.exception(f"Error in moderator {moderator.__class__.__name__}: {e}")
        
        # Combine results based on mode
        flagged = False
        if self.mode == "any":
            flagged = any(result.flagged for result in results)
        elif self.mode == "all":
            flagged = all(result.flagged for result in results) if results else False
        elif self.mode == "majority":
            flagged = sum(1 for result in results if result.flagged) > len(results) / 2
        
        # Combine violations
        all_violations = []
        for result in results:
            all_violations.extend(result.violations)
        
        # Create combined result
        return ModerationResult(
            flagged=flagged,
            violations=all_violations,
            original_text=text,
        )
    
    def add_moderator(self, moderator: BaseContentModerator) -> None:
        """
        Add a moderator to the registry.
        
        Args:
            moderator: Moderator to add
        """
        self.moderators.append(moderator)
    
    def remove_moderator(self, moderator: BaseContentModerator) -> None:
        """
        Remove a moderator from the registry.
        
        Args:
            moderator: Moderator to remove
        """
        if moderator in self.moderators:
            self.moderators.remove(moderator)
