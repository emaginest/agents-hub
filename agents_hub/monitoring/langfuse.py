"""
Langfuse monitoring implementation for the Agents Hub framework.
"""

from typing import Dict, List, Any, Optional, Union
import re
import logging
import json
import asyncio
from langfuse import Langfuse
from agents_hub.monitoring.base import (
    BaseMonitor,
    MonitoringEvent,
    MonitoringLevel,
    EventData,
)
from agents_hub.monitoring.utils import (
    count_tokens,
    count_tokens_for_messages,
    estimate_cost,
)

# Flag to indicate if Langfuse is available
LANGFUSE_AVAILABLE = True
try:
    # Test if Langfuse is properly installed and has the expected API
    test_client = Langfuse(public_key="test", secret_key="test")
    if not hasattr(test_client, "trace") or not callable(test_client.trace):
        LANGFUSE_AVAILABLE = False
except Exception:
    LANGFUSE_AVAILABLE = False

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

        # Check if Langfuse is available with the expected API
        if not LANGFUSE_AVAILABLE:
            logger.warning(
                "Langfuse is not available or has an incompatible API. "
                "Monitoring will be disabled. Please check your Langfuse installation."
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
        # Skip if Langfuse is not available
        if not LANGFUSE_AVAILABLE:
            return None

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

        # Add user_id to metadata if available
        if event_data.user_id:
            metadata["user_id"] = event_data.user_id

        # Create a trace for the conversation using the new API
        try:
            trace_obj = await asyncio.to_thread(
                self.langfuse.trace,
                id=conversation_id,
                name="conversation",
                metadata=metadata,
                release=self.release,
                user_id=event_data.user_id,  # Pass user_id directly to Langfuse
            )
            trace = trace_obj
        except Exception as e:
            logger.exception(f"Error creating trace in Langfuse: {e}")
            return None

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

        # Get the timestamp for the event
        timestamp = event_data.timestamp

        # Create a span for the user message using the new API
        try:
            span = await asyncio.to_thread(
                self.langfuse.span,
                trace_id=trace_id,
                name="user-message",
                input=self._sanitize_text(message),
                metadata=self._sanitize_metadata(event_data.metadata),
                start_time=timestamp,
                end_time=timestamp,  # For user messages, start and end time are the same
            )
        except Exception as e:
            logger.exception(f"Error creating span in Langfuse: {e}")
            return None

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

        # Get the timestamp for the event
        timestamp = event_data.timestamp

        # Create a span for the assistant message using the new API
        try:
            span = await asyncio.to_thread(
                self.langfuse.span,
                trace_id=trace_id,
                name="assistant-message",
                output=self._sanitize_text(message),
                metadata=self._sanitize_metadata(event_data.metadata),
                start_time=timestamp,
                end_time=timestamp,  # For assistant messages, start and end time are the same
            )
        except Exception as e:
            logger.exception(f"Error creating span in Langfuse: {e}")
            return None

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

        # Get the timestamp for the event
        timestamp = event_data.timestamp

        # For tool usage, we need to track when the tool was called and when it returned
        # If output_data is present, it means the tool has completed execution
        # If not, it means the tool is still executing
        has_output = bool(output_data) or error is not None

        # Store the tool call timestamp if this is the initial call
        tool_key = f"{conversation_id}:tool:{tool_name}"
        if not has_output and tool_name not in self.active_spans:
            self.active_spans[f"{tool_key}:start_time"] = timestamp
            start_time = timestamp
            end_time = None  # Tool is still executing
        elif has_output:
            # This is the result of a tool call
            start_time = self.active_spans.get(f"{tool_key}:start_time", timestamp)
            end_time = timestamp  # Tool has completed execution
        else:
            # Default case
            start_time = timestamp
            end_time = timestamp if has_output else None

        # Create a span for the tool usage using the new API
        try:
            span = await asyncio.to_thread(
                self.langfuse.span,
                trace_id=trace_id,
                name=f"tool-{tool_name}",
                input=self._sanitize_data(input_data),
                output=self._sanitize_data(output_data) if has_output else None,
                metadata=self._sanitize_metadata(event_data.metadata),
                start_time=start_time,
                end_time=end_time,
            )

            # Update span with error if present
            if error and hasattr(span, "update"):
                try:
                    await asyncio.to_thread(
                        span.update,
                        status_message=error,
                        level="ERROR",
                    )
                except Exception as e:
                    logger.exception(f"Error updating span in Langfuse: {e}")

            # Clean up stored timestamps if the tool has completed execution
            if has_output and f"{tool_key}:start_time" in self.active_spans:
                del self.active_spans[f"{tool_key}:start_time"]
        except Exception as e:
            logger.exception(f"Error creating span in Langfuse: {e}")
            return None

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

        # Count input tokens if not already provided
        input_tokens = event_data.input_tokens
        if input_tokens is None and messages:
            token_counts = count_tokens_for_messages(messages, model)
            input_tokens = token_counts.get("input_tokens", 0)

        # Prepare metadata with token information
        metadata = self._sanitize_metadata(event_data.metadata)
        if input_tokens is not None:
            metadata["input_tokens"] = input_tokens

        # Store the timestamp when the LLM call was made
        start_time = event_data.timestamp
        self.active_spans[f"{conversation_id}:llm:{provider}:{model}:start_time"] = (
            start_time
        )

        # Create a generation for the LLM call using the new API
        try:
            generation = await asyncio.to_thread(
                self.langfuse.generation,
                trace_id=trace_id,
                name=f"llm-{provider}-{model}",
                model=model,
                model_parameters={
                    "provider": provider,
                },
                input=self._sanitize_data(messages),
                metadata=metadata,
                start_time=start_time,  # Set the start_time explicitly
            )
        except Exception as e:
            logger.exception(f"Error creating generation in Langfuse: {e}")
            return None

        # Store the generation ID and input tokens for later use
        span_key = f"{conversation_id}:llm:{provider}:{model}"
        self.active_spans[span_key] = generation.id

        # Store input tokens for cost calculation when result comes in
        if input_tokens is not None:
            self.active_spans[f"{span_key}:input_tokens"] = input_tokens

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

        # Get token counts from event_data or calculate them
        input_tokens = event_data.input_tokens
        output_tokens = event_data.output_tokens
        total_tokens = event_data.total_tokens
        cost = event_data.cost

        # Find the corresponding generation
        span_key = f"{conversation_id}:llm:{provider}:{model}"
        generation_id = self.active_spans.get(span_key)

        # Get stored input tokens if available
        if input_tokens is None:
            input_tokens = self.active_spans.get(f"{span_key}:input_tokens")

        # Count output tokens if not provided
        if output_tokens is None and result:
            result_str = str(result)
            output_tokens = count_tokens(result_str, model)

        # Calculate total tokens if not provided
        if (
            total_tokens is None
            and input_tokens is not None
            and output_tokens is not None
        ):
            total_tokens = input_tokens + output_tokens

        # Estimate cost if not provided
        if cost is None and input_tokens is not None and output_tokens is not None:
            cost = estimate_cost(provider, model, input_tokens, output_tokens)

        if not generation_id:
            # Create a new generation if we don't have one
            return await self._track_generic_event(event_data)

        # Get the start time of the generation
        start_time = self.active_spans.get(f"{span_key}:start_time")
        # Get the current time as the end time
        end_time = event_data.timestamp

        # Note: We can't directly update the generation in the current Langfuse API
        # The Langfuse Python SDK doesn't have a get_generation method
        # Instead, we'll just create a new span for the result with proper timestamps

        # Create a new span for the result with proper timestamps
        try:
            # Get the trace ID from the conversation ID
            trace_id = self.active_traces.get(conversation_id)
            if not trace_id:
                logger.warning(
                    f"No active trace found for conversation {conversation_id}"
                )
                return None

            # Prepare metadata with token and cost information
            metadata = self._sanitize_metadata(event_data.metadata)
            metadata.update(
                {
                    "provider": provider,
                    "model": model,
                    "generation_id": generation_id,
                }
            )

            # Add token counts and cost to metadata
            if input_tokens is not None:
                metadata["input_tokens"] = input_tokens
            if output_tokens is not None:
                metadata["output_tokens"] = output_tokens
            if total_tokens is not None:
                metadata["total_tokens"] = total_tokens
            if cost is not None:
                metadata["cost"] = cost

            # Create a new span for the result with proper timestamps
            await asyncio.to_thread(
                self.langfuse.span,
                trace_id=trace_id,
                name=f"llm-result-{provider}-{model}",
                output=self._sanitize_data(result),
                metadata=metadata,
                start_time=start_time if start_time else None,
                end_time=end_time,
            )
        except Exception as e:
            logger.exception(f"Error creating result span in Langfuse: {e}")
            return None

        # Remove from active spans
        del self.active_spans[span_key]
        if f"{span_key}:input_tokens" in self.active_spans:
            del self.active_spans[f"{span_key}:input_tokens"]
        if f"{span_key}:start_time" in self.active_spans:
            del self.active_spans[f"{span_key}:start_time"]

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

        # Get the timestamp for the event
        timestamp = event_data.timestamp

        # Create a span for the error using the new API
        try:
            span = await asyncio.to_thread(
                self.langfuse.span,
                trace_id=trace_id,
                name="error",
                input=self._sanitize_text(error),
                metadata=self._sanitize_metadata(event_data.metadata),
                level="ERROR",
                start_time=timestamp,
                end_time=timestamp,  # For errors, start and end time are the same
            )
        except Exception as e:
            logger.exception(f"Error creating span in Langfuse: {e}")
            return None

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

        # Get the timestamp for the event
        timestamp = event_data.timestamp

        # Create a span for the event using the new API
        try:
            span = await asyncio.to_thread(
                self.langfuse.span,
                trace_id=trace_id,
                name=event_data.event_type.value,
                input=self._sanitize_data(event_data.data),
                metadata=self._sanitize_metadata(event_data.metadata),
                start_time=timestamp,
                end_time=timestamp,  # For generic events, start and end time are the same
            )
        except Exception as e:
            logger.exception(f"Error creating span in Langfuse: {e}")
            return None

        return span.id

    async def score_conversation(
        self,
        conversation_id: str,
        name: str,
        value: float,
        comment: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Score a conversation in Langfuse.

        Args:
            conversation_id: ID of the conversation
            name: Name of the score
            value: Score value
            comment: Optional comment
            user_id: Optional ID of the user
        """
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        trace_id = self.active_traces[conversation_id]

        # Create metadata with user information
        metadata = {}
        if user_id:
            metadata["user_id"] = user_id

        # Create a score for the conversation using the new API
        try:
            await asyncio.to_thread(
                self.langfuse.score,
                trace_id=trace_id,
                name=name,
                value=value,
                comment=comment,
                metadata=metadata,
            )
        except Exception as e:
            logger.exception(f"Error creating score in Langfuse: {e}")
            return None

    async def add_user_feedback(
        self,
        conversation_id: str,
        score: int,
        comment: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Add user feedback to a conversation in Langfuse.

        Args:
            conversation_id: ID of the conversation
            score: Feedback score (typically 1-5)
            comment: Optional feedback comment
            user_id: Optional ID of the user
        """
        if not conversation_id or conversation_id not in self.active_traces:
            return None

        trace_id = self.active_traces[conversation_id]

        # Create metadata with user information
        metadata = {}
        if user_id:
            metadata["user_id"] = user_id

        # Create a score for the user feedback
        try:
            await asyncio.to_thread(
                self.langfuse.score,
                trace_id=trace_id,
                name="user_feedback",
                value=float(score),
                comment=comment,
                metadata=metadata,
            )
        except Exception as e:
            logger.exception(f"Error creating user feedback in Langfuse: {e}")
            return None

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
            (
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
                "[EMAIL]",
            ),  # Email
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

    def _sanitize_metadata(
        self, metadata: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
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
