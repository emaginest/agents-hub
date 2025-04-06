"""
Monitoring registry for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import logging
from agents_hub.monitoring.base import BaseMonitor, MonitoringEvent, MonitoringLevel

# Initialize logger
logger = logging.getLogger(__name__)


class MonitoringRegistry(BaseMonitor):
    """
    Registry for managing multiple monitors.
    
    This class allows combining multiple monitors with different configurations.
    """
    
    def __init__(
        self,
        monitors: List[BaseMonitor],
        level: MonitoringLevel = MonitoringLevel.DETAILED,
        include_events: Optional[List[MonitoringEvent]] = None,
        exclude_events: Optional[List[MonitoringEvent]] = None,
    ):
        """
        Initialize the monitoring registry.
        
        Args:
            monitors: List of monitors to use
            level: Monitoring level
            include_events: List of events to include (None for all)
            exclude_events: List of events to exclude (None for none)
        """
        super().__init__(level, include_events, exclude_events)
        self.monitors = monitors
    
    async def _track_event(self, event_data: Any) -> Optional[str]:
        """
        Track an event using all registered monitors.
        
        Args:
            event_data: Event data
            
        Returns:
            Optional event ID from the first monitor
        """
        if not self.monitors:
            return None
        
        # Track the event with all monitors
        results = []
        for monitor in self.monitors:
            try:
                result = await monitor._track_event(event_data)
                results.append(result)
            except Exception as e:
                logger.exception(f"Error in monitor {monitor.__class__.__name__}: {e}")
        
        # Return the first non-None result
        for result in results:
            if result is not None:
                return result
        
        return None
    
    async def score_conversation(
        self,
        conversation_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        """
        Score a conversation using all registered monitors.
        
        Args:
            conversation_id: ID of the conversation
            name: Name of the score
            value: Score value
            comment: Optional comment
        """
        for monitor in self.monitors:
            try:
                if hasattr(monitor, "score_conversation"):
                    await monitor.score_conversation(conversation_id, name, value, comment)
            except Exception as e:
                logger.exception(f"Error scoring conversation in monitor {monitor.__class__.__name__}: {e}")
    
    def add_monitor(self, monitor: BaseMonitor) -> None:
        """
        Add a monitor to the registry.
        
        Args:
            monitor: Monitor to add
        """
        self.monitors.append(monitor)
    
    def remove_monitor(self, monitor: BaseMonitor) -> None:
        """
        Remove a monitor from the registry.
        
        Args:
            monitor: Monitor to remove
        """
        if monitor in self.monitors:
            self.monitors.remove(monitor)
