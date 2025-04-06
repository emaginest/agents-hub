"""
Langfuse monitoring implementation for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import re
import logging
import json
from langfuse import Langfuse
# The AsyncLangfuseClient has been removed or renamed in newer versions
# Using the standard Langfuse client which now supports async operations
from agents_hub.monitoring.base import BaseMonitor, MonitoringEvent, MonitoringLevel, EventData

# Initialize logger
logger = logging.getLogger(__name__)


class LangfuseMonitor(BaseMonitor):
    """
    Monitor for tracking agent interactions using Langfuse.

    This class implements the BaseMonitor interface using Langfuse as the backend.
    """

    def __init__(
        self,
        public_key: str,
        secret_key: str,
        host: str = "https://cloud.langfuse.com",
        release: Optional[str] = None,
        debug: bool = False,
        redact_pii: bool = True,
        level: MonitoringLevel = MonitoringLevel.DETAILED,
        include_events: Optional[List[MonitoringEvent]] = None,
        exclude_events: Optional[List[MonitoringEvent]] = None,
    ):
        """
        Initialize the Langfuse monitor.

        Args:
            public_key: Langfuse public key
            secret_key: Langfuse secret key
            host: Langfuse host URL
            release: Optional release version
            debug: Whether to enable debug mode
            redact_pii: Whether to redact PII from tracked data
            level: Monitoring level
            include_events: List of events to include (None for all)
            exclude_events: List of events to exclude (None for none)
        """
        super().__init__(level, include_events, exclude_events)

        self.langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            debug=debug,
        )

        self.release = release
        self.redact_pii = redact_pii
        self.active_traces = {}
        self.active_spans = {}

    async def _track_event(self, event_data: EventData) -> Optional[str]:
        """
        Track an event using Langfuse.

        Args:
            event_data: Event data

        Returns:
            Optional event ID
        """
        try:
            conversation_id = event_data.conversation_id

            # Handle conversation start/end events
            if event_data.event_type == MonitoringEvent.CONVERSATION_START:
                return await self._start_conversation(event_data)
            elif event_data.event_type == MonitoringEvent.CONVERSATION_END:
                return await self._end_conversation(event_data)

            # For other events, make sure we have an active trace
            if conversation_id and conversation_id not in self.active_traces:
                # Create a trace if it doesn't exist
                await self._start_conversation(event_data)

            # Handle specific event types
            if event_data.event_type == MonitoringEvent.USER_MESSAGE:
                return await self._track_user_message(event_data)
            elif event_data.event_type == MonitoringEvent.ASSISTANT_MESSAGE:
                return await self._track_assistant_message(event_data)
            elif event_data.event_type == MonitoringEvent.TOOL_CALL:
                return await self._track_tool_usage(event_data)
            elif event_data.event_type == MonitoringEvent.LLM_CALL:
                return await self._track_llm_call(event_data)
            elif event_data.event_type == MonitoringEvent.LLM_RESULT:
                return await self._track_llm_result(event_data)
            elif event_data.event_type == MonitoringEvent.ERROR:
                return await self._track_error(event_data)
            else:
                # Generic event tracking
                return await self._track_generic_event(event_data)

        except Exception as e:
            logger.exception(f"Error tracking event in Langfuse: {e}")
            return None

    async def _start_conversation(self, event_data: EventData) -> str:
        """
        Start a conversation trace in Langfuse.

        Args:
            event_data: Event data

        Returns:
            Trace ID
        """
        conversation_id = event_data.conversation_id
        if not conversation_id:
            return None

        # Create a trace for the conversation
        metadata = self._sanitize_metadata(event_data.metadata)
        metadata["agent_name"] = event_data.agent_name

        trace = await self.langfuse.trace.create(
            id=conversation_id,
            name="conversation",
            metadata=metadata,
            release=self.release,
        )

        self.active_traces[conversation_id] = trace.id
        return trace.id

    async def _end_conversation(self, event_data: EventData) -> None:
        """
        End a conversation trace in Langfuse.

        Args:
            event_data: Event data

        Returns:
            None
        """
        conversation_id = event_data.conversation_id
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        # End the trace
        trace_id = self.active_traces[conversation_id]

        # Remove from active traces
        del self.active_traces[conversation_id]

        # Remove any active spans for this conversation
        spans_to_remove = []
        for span_key in self.active_spans:
            if span_key.startswith(f"{conversation_id}:"):
                spans_to_remove.append(span_key)

        for span_key in spans_to_remove:
            del self.active_spans[span_key]

        return trace_id

    async def _track_user_message(self, event_data: EventData) -> str:
        """
        Track a user message in Langfuse.

        Args:
            event_data: Event data

        Returns:
            Span ID
        """
        conversation_id = event_data.conversation_id
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        trace_id = self.active_traces[conversation_id]
        message = event_data.data.get("message", "")

        # Create a span for the user message
        span = await self.langfuse.span.create(
            trace_id=trace_id,
            name="user-message",
            input=self._sanitize_text(message),
            metadata=self._sanitize_metadata(event_data.metadata),
        )

        return span.id

    async def _track_assistant_message(self, event_data: EventData) -> str:
        """
        Track an assistant message in Langfuse.

        Args:
            event_data: Event data

        Returns:
            Span ID
        """
        conversation_id = event_data.conversation_id
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        trace_id = self.active_traces[conversation_id]
        message = event_data.data.get("message", "")

        # Create a span for the assistant message
        span = await self.langfuse.span.create(
            trace_id=trace_id,
            name="assistant-message",
            output=self._sanitize_text(message),
            metadata=self._sanitize_metadata(event_data.metadata),
        )

        return span.id

    async def _track_tool_usage(self, event_data: EventData) -> str:
        """
        Track tool usage in Langfuse.

        Args:
            event_data: Event data

        Returns:
            Span ID
        """
        conversation_id = event_data.conversation_id
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        trace_id = self.active_traces[conversation_id]
        tool_name = event_data.data.get("tool_name", "unknown-tool")
        input_data = event_data.data.get("input", {})
        output_data = event_data.data.get("output", {})
        error = event_data.data.get("error")

        # Create a span for the tool usage
        span = await self.langfuse.span.create(
            trace_id=trace_id,
            name=f"tool-{tool_name}",
            input=self._sanitize_data(input_data),
            output=self._sanitize_data(output_data),
            metadata=self._sanitize_metadata(event_data.metadata),
        )

        # Update span with error if present
        if error:
            await self.langfuse.span.update(
                id=span.id,
                status_message=error,
                level="ERROR",
            )

        return span.id

    async def _track_llm_call(self, event_data: EventData) -> str:
        """
        Track an LLM call in Langfuse.

        Args:
            event_data: Event data

        Returns:
            Span ID
        """
        conversation_id = event_data.conversation_id
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        trace_id = self.active_traces[conversation_id]
        provider = event_data.data.get("provider", "unknown")
        model = event_data.data.get("model", "unknown")
        messages = event_data.data.get("messages", [])

        # Create a generation for the LLM call
        generation = await self.langfuse.generation.create(
            trace_id=trace_id,
            name=f"llm-{provider}-{model}",
            model=model,
            model_parameters={
                "provider": provider,
            },
            input=self._sanitize_data(messages),
            metadata=self._sanitize_metadata(event_data.metadata),
        )

        # Store the generation ID for later use
        span_key = f"{conversation_id}:llm:{provider}:{model}"
        self.active_spans[span_key] = generation.id

        return generation.id

    async def _track_llm_result(self, event_data: EventData) -> str:
        """
        Track an LLM result in Langfuse.

        Args:
            event_data: Event data

        Returns:
            Span ID
        """
        conversation_id = event_data.conversation_id
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        provider = event_data.data.get("provider", "unknown")
        model = event_data.data.get("model", "unknown")
        result = event_data.data.get("result", {})

        # Find the corresponding generation
        span_key = f"{conversation_id}:llm:{provider}:{model}"
        generation_id = self.active_spans.get(span_key)

        if not generation_id:
            # Create a new generation if we don't have one
            return await self._track_generic_event(event_data)

        # Update the generation with the result
        await self.langfuse.generation.update(
            id=generation_id,
            output=self._sanitize_data(result),
        )

        # Remove from active spans
        del self.active_spans[span_key]

        return generation_id

    async def _track_error(self, event_data: EventData) -> str:
        """
        Track an error in Langfuse.

        Args:
            event_data: Event data

        Returns:
            Span ID
        """
        conversation_id = event_data.conversation_id
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        trace_id = self.active_traces[conversation_id]
        error = event_data.data.get("error", "Unknown error")

        # Create a span for the error
        span = await self.langfuse.span.create(
            trace_id=trace_id,
            name="error",
            input=self._sanitize_text(error),
            metadata=self._sanitize_metadata(event_data.metadata),
            level="ERROR",
        )

        return span.id

    async def _track_generic_event(self, event_data: EventData) -> str:
        """
        Track a generic event in Langfuse.

        Args:
            event_data: Event data

        Returns:
            Span ID
        """
        conversation_id = event_data.conversation_id
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        trace_id = self.active_traces[conversation_id]

        # Create a span for the event
        span = await self.langfuse.span.create(
            trace_id=trace_id,
            name=event_data.event_type.value,
            input=self._sanitize_data(event_data.data),
            metadata=self._sanitize_metadata(event_data.metadata),
        )

        return span.id

    async def score_conversation(
        self,
        conversation_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None,
    ) -> None:
        """
        Score a conversation in Langfuse.

        Args:
            conversation_id: ID of the conversation
            name: Name of the score
            value: Score value
            comment: Optional comment
        """
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        trace_id = self.active_traces[conversation_id]

        # Create a score for the conversation
        await self.langfuse.score.create(
            trace_id=trace_id,
            name=name,
            value=value,
            comment=comment,
        )

    def _sanitize_text(self, text: str) -> str:
        """
        Sanitize text by redacting PII if enabled.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        if not self.redact_pii or not text or not isinstance(text, str):
            return text

        # Implement PII redaction logic
        redacted_text = text
        patterns = [
            (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),  # Email
            (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]"),  # Phone number
            (r"\b\d{3}[-]?\d{2}[-]?\d{4}\b", "[SSN]"),  # SSN
            (r"\b(?:\d[ -]*?){13,16}\b", "[CREDIT_CARD]"),  # Credit card
        ]

        for pattern, replacement in patterns:
            redacted_text = re.sub(pattern, replacement, redacted_text)

        return redacted_text

    def _sanitize_data(self, data: Any) -> Any:
        """
        Sanitize data by redacting PII if enabled.

        Args:
            data: Data to sanitize

        Returns:
            Sanitized data
        """
        if not self.redact_pii:
            return data

        if isinstance(data, str):
            return self._sanitize_text(data)
        elif isinstance(data, dict):
            return {k: self._sanitize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        else:
            return data

    def _sanitize_metadata(self, metadata: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Sanitize metadata by redacting PII if enabled.

        Args:
            metadata: Metadata to sanitize

        Returns:
            Sanitized metadata
        """
        if not metadata or not self.redact_pii:
            return metadata

        return self._sanitize_data(metadata)
