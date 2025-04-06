"""
Base Memory interface for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    """A single memory entry."""
    user_message: str = Field(..., description="Message from the user")
    assistant_message: str = Field(..., description="Response from the assistant")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this interaction occurred")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for this interaction")


class BaseMemory:
    """
    Base class for memory providers.
    
    This abstract class defines the interface that all memory providers must implement.
    """
    
    async def add_interaction(
        self,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add a new interaction to memory.
        
        Args:
            conversation_id: Identifier for the conversation
            user_message: Message from the user
            assistant_message: Response from the assistant
            metadata: Optional additional metadata
        """
        raise NotImplementedError("Subclasses must implement add_interaction()")
    
    async def get_history(
        self,
        conversation_id: str,
        limit: int = 10,
        before: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history from memory.
        
        Args:
            conversation_id: Identifier for the conversation
            limit: Maximum number of interactions to retrieve
            before: Only retrieve interactions before this time
            
        Returns:
            List of interactions
        """
        raise NotImplementedError("Subclasses must implement get_history()")
    
    async def clear_history(self, conversation_id: str) -> None:
        """
        Clear conversation history from memory.
        
        Args:
            conversation_id: Identifier for the conversation
        """
        raise NotImplementedError("Subclasses must implement clear_history()")
    
    async def search_memory(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search memory for relevant interactions.
        
        Args:
            query: Search query
            conversation_id: Optional conversation ID to limit search to
            limit: Maximum number of results to return
            
        Returns:
            List of relevant interactions
        """
        raise NotImplementedError("Subclasses must implement search_memory()")
    
    async def get_statistics(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about the memory.
        
        Args:
            conversation_id: Optional conversation ID to limit statistics to
            
        Returns:
            Dictionary of statistics
        """
        raise NotImplementedError("Subclasses must implement get_statistics()")
