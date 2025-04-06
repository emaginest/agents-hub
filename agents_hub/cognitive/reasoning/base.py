"""
Base reasoning interface for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
from abc import ABC, abstractmethod

# Initialize logger
logger = logging.getLogger(__name__)


class BaseReasoning(ABC):
    """
    Base class for reasoning mechanisms.
    
    This abstract class defines the interface that all reasoning
    mechanisms must implement.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the reasoning mechanism.
        
        Args:
            name: Name of the reasoning mechanism
            description: Description of the reasoning mechanism
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    async def apply(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply the reasoning mechanism.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Reasoning results
        """
        pass
    
    @abstractmethod
    def get_suitability(
        self,
        memory_state: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        """
        Get the suitability of this reasoning mechanism for the current state.
        
        Args:
            memory_state: Current state of working memory
            context: Context information
            
        Returns:
            Suitability score (0.0 to 1.0)
        """
        pass
    
    def _extract_input(self, memory_state: Dict[str, Any]) -> str:
        """
        Extract input text from memory state.
        
        Args:
            memory_state: Current state of working memory
            
        Returns:
            Input text
        """
        # Look for input item
        for item in memory_state.get("items", []):
            if item["type"] == "input":
                return item["content"]
        
        # If no input item found, return empty string
        return ""
    
    def _extract_active_items(self, memory_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract active items from memory state.
        
        Args:
            memory_state: Current state of working memory
            
        Returns:
            List of active items
        """
        return memory_state.get("active_items", [])
