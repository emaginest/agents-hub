"""
Base moderation interface for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field


class ModerationCategory(str, Enum):
    """Categories for content moderation."""
    HATE = "hate"
    HARASSMENT = "harassment"
    SEXUAL = "sexual"
    VIOLENCE = "violence"
    SELF_HARM = "self_harm"
    ILLEGAL = "illegal"
    JAILBREAK = "jailbreak"
    PROMPT_INJECTION = "prompt_injection"
    CUSTOM = "custom"


class ModerationViolation(BaseModel):
    """Represents a moderation violation."""
    category: ModerationCategory = Field(..., description="Category of the violation")
    severity: float = Field(1.0, description="Severity score (0.0 to 1.0)")
    description: str = Field("", description="Description of the violation")
    source: str = Field("", description="Source of the moderation decision")


class ModerationResult(BaseModel):
    """Result of content moderation."""
    flagged: bool = Field(False, description="Whether the content was flagged")
    violations: List[ModerationViolation] = Field(default_factory=list, description="List of violations")
    original_text: str = Field("", description="Original text that was moderated")
    
    @property
    def has_violations(self) -> bool:
        """Check if there are any violations."""
        return self.flagged and len(self.violations) > 0
    
    @property
    def highest_severity(self) -> float:
        """Get the highest severity among violations."""
        if not self.violations:
            return 0.0
        return max(v.severity for v in self.violations)
    
    def get_violations_by_category(self, category: ModerationCategory) -> List[ModerationViolation]:
        """Get violations by category."""
        return [v for v in self.violations if v.category == category]


class BaseContentModerator:
    """
    Base class for content moderators.
    
    This abstract class defines the interface that all content moderators must implement.
    """
    
    async def moderate(self, text: str) -> ModerationResult:
        """
        Moderate the given text.
        
        Args:
            text: Text to moderate
            
        Returns:
            ModerationResult object containing the moderation decision
        """
        raise NotImplementedError("Subclasses must implement moderate()")
    
    async def is_safe(self, text: str) -> bool:
        """
        Check if the given text is safe.
        
        Args:
            text: Text to check
            
        Returns:
            True if the text is safe, False otherwise
        """
        result = await self.moderate(text)
        return not result.flagged
