"""
OpenAI-based content moderation for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import aiohttp
from agents_hub.moderation.base import BaseContentModerator, ModerationResult, ModerationViolation, ModerationCategory


# Initialize logger
logger = logging.getLogger(__name__)


# OpenAI category mapping
OPENAI_CATEGORY_MAPPING = {
    "sexual": ModerationCategory.SEXUAL,
    "hate": ModerationCategory.HATE,
    "harassment": ModerationCategory.HARASSMENT,
    "self-harm": ModerationCategory.SELF_HARM,
    "sexual/minors": ModerationCategory.SEXUAL,
    "hate/threatening": ModerationCategory.HATE,
    "violence": ModerationCategory.VIOLENCE,
    "violence/graphic": ModerationCategory.VIOLENCE,
    "self-harm/intent": ModerationCategory.SELF_HARM,
    "self-harm/instructions": ModerationCategory.SELF_HARM,
    "harassment/threatening": ModerationCategory.HARASSMENT,
    "illegal": ModerationCategory.ILLEGAL,
}


class OpenAIModerator(BaseContentModerator):
    """
    OpenAI-based content moderator.
    
    This class implements content moderation using OpenAI's moderation API.
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        categories: Optional[List[str]] = None,
    ):
        """
        Initialize the OpenAI moderator.
        
        Args:
            api_key: OpenAI API key
            base_url: Base URL for OpenAI API
            categories: List of categories to check (None for all)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.categories = categories
    
    async def moderate(self, text: str) -> ModerationResult:
        """
        Moderate the given text using OpenAI's moderation API.
        
        Args:
            text: Text to moderate
            
        Returns:
            ModerationResult object containing the moderation decision
        """
        try:
            # Call OpenAI moderation API
            moderation_result = await self._call_moderation_api(text)
            
            # Process the result
            if moderation_result is None:
                # API call failed, return safe result
                return ModerationResult(
                    flagged=False,
                    violations=[],
                    original_text=text,
                )
            
            # Extract violations
            violations = []
            if "results" in moderation_result and len(moderation_result["results"]) > 0:
                result = moderation_result["results"][0]
                
                # Check if content is flagged
                flagged = result.get("flagged", False)
                
                # If flagged, extract categories
                if flagged:
                    categories = result.get("categories", {})
                    scores = result.get("category_scores", {})
                    
                    for category, is_flagged in categories.items():
                        # Skip if not flagged or not in requested categories
                        if not is_flagged:
                            continue
                        
                        if self.categories and category not in self.categories:
                            continue
                        
                        # Get score
                        score = scores.get(category, 0.0)
                        
                        # Map to internal category
                        internal_category = OPENAI_CATEGORY_MAPPING.get(
                            category, ModerationCategory.CUSTOM
                        )
                        
                        # Add violation
                        violations.append(
                            ModerationViolation(
                                category=internal_category,
                                severity=score,
                                description=f"OpenAI moderation flagged content as {category}",
                                source="openai",
                            )
                        )
            
            # Create result
            return ModerationResult(
                flagged=len(violations) > 0,
                violations=violations,
                original_text=text,
            )
        
        except Exception as e:
            logger.exception(f"Error in OpenAI moderation: {e}")
            # Return safe result on error
            return ModerationResult(
                flagged=False,
                violations=[],
                original_text=text,
            )
    
    async def _call_moderation_api(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Call OpenAI's moderation API.
        
        Args:
            text: Text to moderate
            
        Returns:
            API response or None if the call failed
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        data = {"input": text}
        url = f"{self.base_url}/moderations"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Moderation API request failed: {response.status}")
                        return None
        except Exception as e:
            logger.exception(f"Error calling moderation API: {e}")
            return None
