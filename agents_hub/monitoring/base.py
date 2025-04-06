"""
Base monitoring interface for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
import time
import uuid
from pydantic import BaseModel, Field


class MonitoringLevel(str, Enum):
    """Monitoring level for the monitoring system."""
    BASIC = "basic"  # Track only basic events (conversations, messages)
    DETAILED = "detailed"  # Track detailed events (tools, memory)
    COMPREHENSIVE = "comprehensive"  # Track all events (including internal operations)


class MonitoringEvent(str, Enum):
    """Event types for the monitoring system."""
    CONVERSATION_START = "conversation_start"
    CONVERSATION_END = "conversation_end"
    USER_MESSAGE = "user_message"
    ASSISTANT_MESSAGE = "assistant_message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    MEMORY_READ = "memory_read"
    MEMORY_WRITE = "memory_write"
    LLM_CALL = "llm_call"
    LLM_RESULT = "llm_result"
    ERROR = "error"
    CUSTOM = "custom"


class EventData(BaseModel):
    """Data for a monitoring event."""
    event_type: MonitoringEvent = Field(..., description="Type of the event")
    timestamp: float = Field(default_factory=time.time, description="Timestamp of the event")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation")
    agent_name: Optional[str] = Field(None, description="Name of the agent")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Event metadata")


class BaseMonitor:
    """
    Base class for monitoring systems.
    
    This abstract class defines the interface that all monitoring systems must implement.
    """
    
    def __init__(
        self,
        level: MonitoringLevel = MonitoringLevel.DETAILED,
        include_events: Optional[List[MonitoringEvent]] = None,
        exclude_events: Optional[List[MonitoringEvent]] = None,
    ):
        """
        Initialize the monitor.
        
        Args:
            level: Monitoring level
            include_events: List of events to include (None for all)
            exclude_events: List of events to exclude (None for none)
        """
        self.level = level
        self.include_events = include_events
        self.exclude_events = exclude_events
    
    def should_track(self, event_type: MonitoringEvent) -> bool:
        """
        Check if an event should be tracked.
        
        Args:
            event_type: Type of the event
            
        Returns:
            True if the event should be tracked, False otherwise
        """
        # Check if event is explicitly excluded
        if self.exclude_events and event_type in self.exclude_events:
            return False
        
        # Check if event is explicitly included
        if self.include_events and event_type not in self.include_events:
            return False
        
        # Check monitoring level
        if self.level == MonitoringLevel.BASIC:
            return event_type in [
                MonitoringEvent.CONVERSATION_START,
                MonitoringEvent.CONVERSATION_END,
                MonitoringEvent.USER_MESSAGE,
                MonitoringEvent.ASSISTANT_MESSAGE,
                MonitoringEvent.ERROR,
            ]
        elif self.level == MonitoringLevel.DETAILED:
            return event_type != MonitoringEvent.CUSTOM
        else:  # COMPREHENSIVE
            return True
    
    async def track_event(
        self,
        event_type: MonitoringEvent,
        conversation_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Track an event.
        
        Args:
            event_type: Type of the event
            conversation_id: Optional ID of the conversation
            agent_name: Optional name of the agent
            data: Optional event data
            metadata: Optional event metadata
            
        Returns:
            Optional event ID
        """
        if not self.should_track(event_type):
            return None
        
        event_data = EventData(
            event_type=event_type,
            conversation_id=conversation_id,
            agent_name=agent_name,
            data=data or {},
            metadata=metadata or {},
        )
        
        return await self._track_event(event_data)
    
    async def _track_event(self, event_data: EventData) -> Optional[str]:
        """
        Track an event (implementation).
        
        Args:
            event_data: Event data
            
        Returns:
            Optional event ID
        """
        raise NotImplementedError("Subclasses must implement _track_event()")
    
    async def start_conversation(
        self,
        conversation_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start tracking a conversation.
        
        Args:
            conversation_id: Optional ID of the conversation (generated if not provided)
            agent_name: Optional name of the agent
            metadata: Optional metadata for the conversation
            
        Returns:
            Conversation ID
        """
        conversation_id = conversation_id or str(uuid.uuid4())
        
        await self.track_event(
            event_type=MonitoringEvent.CONVERSATION_START,
            conversation_id=conversation_id,
            agent_name=agent_name,
            metadata=metadata,
        )
        
        return conversation_id
    
    async def end_conversation(
        self,
        conversation_id: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        End tracking a conversation.
        
        Args:
            conversation_id: ID of the conversation
            agent_name: Optional name of the agent
            metadata: Optional metadata for the conversation
        """
        await self.track_event(
            event_type=MonitoringEvent.CONVERSATION_END,
            conversation_id=conversation_id,
            agent_name=agent_name,
            metadata=metadata,
        )
    
    async def track_user_message(
        self,
        message: str,
        conversation_id: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Track a user message.
        
        Args:
            message: User message
            conversation_id: ID of the conversation
            agent_name: Optional name of the agent
            metadata: Optional metadata for the message
            
        Returns:
            Optional event ID
        """
        return await self.track_event(
            event_type=MonitoringEvent.USER_MESSAGE,
            conversation_id=conversation_id,
            agent_name=agent_name,
            data={"message": message},
            metadata=metadata,
        )
    
    async def track_assistant_message(
        self,
        message: str,
        conversation_id: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Track an assistant message.
        
        Args:
            message: Assistant message
            conversation_id: ID of the conversation
            agent_name: Optional name of the agent
            metadata: Optional metadata for the message
            
        Returns:
            Optional event ID
        """
        return await self.track_event(
            event_type=MonitoringEvent.ASSISTANT_MESSAGE,
            conversation_id=conversation_id,
            agent_name=agent_name,
            data={"message": message},
            metadata=metadata,
        )
    
    async def track_tool_usage(
        self,
        tool_name: str,
        input_data: Any,
        output_data: Any,
        conversation_id: str,
        agent_name: Optional[str] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Track tool usage.
        
        Args:
            tool_name: Name of the tool
            input_data: Input data for the tool
            output_data: Output data from the tool
            conversation_id: ID of the conversation
            agent_name: Optional name of the agent
            error: Optional error message
            metadata: Optional metadata for the tool usage
            
        Returns:
            Optional event ID
        """
        data = {
            "tool_name": tool_name,
            "input": input_data,
            "output": output_data,
        }
        
        if error:
            data["error"] = error
        
        return await self.track_event(
            event_type=MonitoringEvent.TOOL_CALL,
            conversation_id=conversation_id,
            agent_name=agent_name,
            data=data,
            metadata=metadata,
        )
    
    async def track_llm_call(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, Any]],
        conversation_id: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Track an LLM call.
        
        Args:
            provider: LLM provider name
            model: LLM model name
            messages: Messages sent to the LLM
            conversation_id: ID of the conversation
            agent_name: Optional name of the agent
            metadata: Optional metadata for the LLM call
            
        Returns:
            Optional event ID
        """
        return await self.track_event(
            event_type=MonitoringEvent.LLM_CALL,
            conversation_id=conversation_id,
            agent_name=agent_name,
            data={
                "provider": provider,
                "model": model,
                "messages": messages,
            },
            metadata=metadata,
        )
    
    async def track_llm_result(
        self,
        provider: str,
        model: str,
        result: Any,
        conversation_id: str,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Track an LLM result.
        
        Args:
            provider: LLM provider name
            model: LLM model name
            result: Result from the LLM
            conversation_id: ID of the conversation
            agent_name: Optional name of the agent
            metadata: Optional metadata for the LLM result
            
        Returns:
            Optional event ID
        """
        return await self.track_event(
            event_type=MonitoringEvent.LLM_RESULT,
            conversation_id=conversation_id,
            agent_name=agent_name,
            data={
                "provider": provider,
                "model": model,
                "result": result,
            },
            metadata=metadata,
        )
    
    async def track_error(
        self,
        error: str,
        conversation_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Track an error.
        
        Args:
            error: Error message
            conversation_id: Optional ID of the conversation
            agent_name: Optional name of the agent
            metadata: Optional metadata for the error
            
        Returns:
            Optional event ID
        """
        return await self.track_event(
            event_type=MonitoringEvent.ERROR,
            conversation_id=conversation_id,
            agent_name=agent_name,
            data={"error": error},
            metadata=metadata,
        )
    
    async def track_custom_event(
        self,
        event_name: str,
        data: Any,
        conversation_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Track a custom event.
        
        Args:
            event_name: Name of the event
            data: Event data
            conversation_id: Optional ID of the conversation
            agent_name: Optional name of the agent
            metadata: Optional metadata for the event
            
        Returns:
            Optional event ID
        """
        metadata = metadata or {}
        metadata["event_name"] = event_name
        
        return await self.track_event(
            event_type=MonitoringEvent.CUSTOM,
            conversation_id=conversation_id,
            agent_name=agent_name,
            data=data,
            metadata=metadata,
        )
