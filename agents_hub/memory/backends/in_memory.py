"""
In-memory memory backend for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from agents_hub.memory.base import BaseMemory


class InMemoryMemory(BaseMemory):
    """
    In-memory memory backend.
    
    This class implements the BaseMemory interface using in-memory storage.
    It's useful for testing and development, but data is lost when the process ends.
    """
    
    def __init__(self):
        """Initialize the in-memory memory backend."""
        self.memory = {}  # conversation_id -> list of interactions
    
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
        if conversation_id not in self.memory:
            self.memory[conversation_id] = []
        
        self.memory[conversation_id].append({
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "user_message": user_message,
            "assistant_message": assistant_message,
            "timestamp": datetime.now(),
            "metadata": metadata or {},
        })
    
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
        if conversation_id not in self.memory:
            return []
        
        history = self.memory[conversation_id]
        
        if before:
            history = [item for item in history if item["timestamp"] < before]
        
        # Sort by timestamp (newest first)
        history = sorted(history, key=lambda x: x["timestamp"], reverse=True)
        
        # Apply limit
        history = history[:limit]
        
        # Return in chronological order
        return list(reversed(history))
    
    async def clear_history(self, conversation_id: str) -> None:
        """
        Clear conversation history from memory.
        
        Args:
            conversation_id: Identifier for the conversation
        """
        if conversation_id in self.memory:
            del self.memory[conversation_id]
    
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
        # Simple implementation: just search for substring matches
        results = []
        
        # Determine which conversations to search
        conversations = [conversation_id] if conversation_id else self.memory.keys()
        
        for conv_id in conversations:
            if conv_id not in self.memory:
                continue
            
            for interaction in self.memory[conv_id]:
                # Check if query is in user message or assistant message
                if (query.lower() in interaction["user_message"].lower() or
                    query.lower() in interaction["assistant_message"].lower()):
                    results.append(interaction)
                    
                    # Break if we've reached the limit
                    if len(results) >= limit:
                        break
            
            # Break if we've reached the limit
            if len(results) >= limit:
                break
        
        return results
    
    async def get_statistics(self, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about the memory.
        
        Args:
            conversation_id: Optional conversation ID to limit statistics to
            
        Returns:
            Dictionary of statistics
        """
        stats = {
            "total_conversations": len(self.memory),
            "total_interactions": sum(len(interactions) for interactions in self.memory.values()),
        }
        
        if conversation_id:
            if conversation_id in self.memory:
                stats["conversation_interactions"] = len(self.memory[conversation_id])
                stats["conversation_exists"] = True
            else:
                stats["conversation_interactions"] = 0
                stats["conversation_exists"] = False
        
        return stats
