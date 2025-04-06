"""
Working memory system for the cognitive architecture.
"""

from typing import Dict, List, Any, Optional, Union
import logging
import time

# Initialize logger
logger = logging.getLogger(__name__)


class WorkingMemory:
    """
    Working memory system for active information storage.
    
    This class provides a limited capacity memory system for storing
    and manipulating information during cognitive processing.
    """
    
    def __init__(
        self,
        capacity: int = 7,  # Miller's Law: 7 ± 2 items
        decay_rate: float = 0.1,
        chunking_enabled: bool = True,
        prioritization_enabled: bool = True,
    ):
        """
        Initialize the working memory system.
        
        Args:
            capacity: Maximum number of items in working memory
            decay_rate: Rate at which items decay over time
            chunking_enabled: Whether to enable chunking
            prioritization_enabled: Whether to enable prioritization
        """
        self.capacity = capacity
        self.decay_rate = decay_rate
        self.chunking_enabled = chunking_enabled
        self.prioritization_enabled = prioritization_enabled
        
        # Initialize memory state
        self.items = []
        self.last_update_time = time.time()
    
    async def update(
        self,
        perception_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update working memory with new information.
        
        Args:
            perception_result: Result of perception processing
            context: Context information
            
        Returns:
            Current state of working memory
        """
        # Apply decay to existing items
        current_time = time.time()
        time_elapsed = current_time - self.last_update_time
        self._apply_decay(time_elapsed)
        self.last_update_time = current_time
        
        # Extract new items from perception result
        new_items = self._extract_items(perception_result)
        
        # Apply chunking if enabled
        if self.chunking_enabled:
            new_items = self._apply_chunking(new_items)
        
        # Add new items to memory
        for item in new_items:
            self._add_item(item)
        
        # Apply prioritization if enabled
        if self.prioritization_enabled:
            self._apply_prioritization(context)
        
        # Enforce capacity limit
        self._enforce_capacity()
        
        # Return current memory state
        return self._get_memory_state()
    
    def _apply_decay(self, time_elapsed: float) -> None:
        """
        Apply decay to existing items.
        
        Args:
            time_elapsed: Time elapsed since last update
        """
        for item in self.items:
            # Reduce activation by decay rate * time elapsed
            item["activation"] -= self.decay_rate * time_elapsed
            
            # Ensure activation doesn't go below 0
            item["activation"] = max(0.0, item["activation"])
    
    def _extract_items(self, perception_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract items from perception result.
        
        Args:
            perception_result: Result of perception processing
            
        Returns:
            List of extracted items
        """
        items = []
        
        # Extract entities as items
        if "features" in perception_result and "entities" in perception_result["features"]:
            for entity in perception_result["features"]["entities"]:
                items.append({
                    "type": "entity",
                    "content": entity,
                    "activation": 1.0,
                    "source": "perception",
                })
        
        # Extract keywords as items
        if "features" in perception_result and "keywords" in perception_result["features"]:
            for keyword in perception_result["features"]["keywords"]:
                items.append({
                    "type": "keyword",
                    "content": keyword,
                    "activation": 0.8,
                    "source": "perception",
                })
        
        # Extract main topic as item
        if "attention_focus" in perception_result and "main_topic" in perception_result["attention_focus"]:
            main_topic = perception_result["attention_focus"]["main_topic"]
            if main_topic:
                items.append({
                    "type": "topic",
                    "content": main_topic,
                    "activation": 1.0,
                    "source": "perception",
                })
        
        # Extract domain as item
        if "context_info" in perception_result and "domain" in perception_result["context_info"]:
            domain = perception_result["context_info"]["domain"]
            if domain and domain != "general" and domain != "mixed":
                items.append({
                    "type": "domain",
                    "content": domain,
                    "activation": 0.9,
                    "source": "perception",
                })
        
        # Extract task type as item
        if "context_info" in perception_result and "task_type" in perception_result["context_info"]:
            task_type = perception_result["context_info"]["task_type"]
            if task_type and task_type != "general":
                items.append({
                    "type": "task_type",
                    "content": task_type,
                    "activation": 0.9,
                    "source": "perception",
                })
        
        # Extract original input as item
        if "original_input" in perception_result:
            items.append({
                "type": "input",
                "content": perception_result["original_input"],
                "activation": 1.0,
                "source": "perception",
            })
        
        return items
    
    def _apply_chunking(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Apply chunking to items.
        
        Args:
            items: Items to chunk
            
        Returns:
            Chunked items
        """
        # Simple chunking: group related items
        chunked_items = []
        
        # Group entities and keywords
        entities = [item for item in items if item["type"] == "entity"]
        keywords = [item for item in items if item["type"] == "keyword"]
        
        if entities and len(entities) > 2:
            # Create a chunk for entities
            chunk_content = ", ".join(item["content"] for item in entities)
            chunked_items.append({
                "type": "chunk",
                "content": chunk_content,
                "activation": 1.0,
                "source": "chunking",
                "items": entities,
            })
        else:
            chunked_items.extend(entities)
        
        if keywords and len(keywords) > 3:
            # Create a chunk for keywords
            chunk_content = ", ".join(item["content"] for item in keywords)
            chunked_items.append({
                "type": "chunk",
                "content": chunk_content,
                "activation": 0.8,
                "source": "chunking",
                "items": keywords,
            })
        else:
            chunked_items.extend(keywords)
        
        # Add other items unchanged
        other_items = [item for item in items if item["type"] not in ["entity", "keyword"]]
        chunked_items.extend(other_items)
        
        return chunked_items
    
    def _add_item(self, item: Dict[str, Any]) -> None:
        """
        Add an item to working memory.
        
        Args:
            item: Item to add
        """
        # Check if item already exists
        for existing_item in self.items:
            if (
                existing_item["type"] == item["type"] and
                existing_item["content"] == item["content"]
            ):
                # Update activation
                existing_item["activation"] = max(existing_item["activation"], item["activation"])
                return
        
        # Add new item
        self.items.append(item)
    
    def _apply_prioritization(self, context: Dict[str, Any]) -> None:
        """
        Apply prioritization to items.
        
        Args:
            context: Context information
        """
        # Prioritize based on recency
        for i, item in enumerate(self.items):
            # More recent items (higher index) get higher activation
            recency_boost = i / max(len(self.items), 1)
            item["activation"] += recency_boost * 0.1
        
        # Prioritize based on relevance to context
        if "relevant_topics" in context:
            relevant_topics = context["relevant_topics"]
            for item in self.items:
                if item["content"].lower() in [topic.lower() for topic in relevant_topics]:
                    item["activation"] += 0.2
        
        # Prioritize based on item type
        type_priorities = {
            "input": 0.3,
            "topic": 0.2,
            "entity": 0.1,
            "domain": 0.1,
            "task_type": 0.1,
            "chunk": 0.1,
            "keyword": 0.05,
        }
        
        for item in self.items:
            if item["type"] in type_priorities:
                item["activation"] += type_priorities[item["type"]]
    
    def _enforce_capacity(self) -> None:
        """
        Enforce capacity limit by removing low-activation items.
        """
        if len(self.items) <= self.capacity:
            return
        
        # Sort items by activation (descending)
        self.items.sort(key=lambda item: item["activation"], reverse=True)
        
        # Keep only the top items
        self.items = self.items[:self.capacity]
    
    def _get_memory_state(self) -> Dict[str, Any]:
        """
        Get current state of working memory.
        
        Returns:
            Memory state
        """
        # Sort items by activation (descending)
        sorted_items = sorted(self.items, key=lambda item: item["activation"], reverse=True)
        
        # Extract active items (activation > 0.5)
        active_items = [item for item in sorted_items if item["activation"] > 0.5]
        
        # Extract semi-active items (0 < activation <= 0.5)
        semi_active_items = [item for item in sorted_items if 0 < item["activation"] <= 0.5]
        
        # Create memory state
        memory_state = {
            "items": sorted_items,
            "active_items": active_items,
            "semi_active_items": semi_active_items,
            "capacity": self.capacity,
            "usage": len(self.items),
            "main_focus": active_items[0]["content"] if active_items else None,
        }
        
        return memory_state
