from langfuse.openai import openai as langfuse_openai
from langfuse import Langfuse
import logging
import time
from app.config import Settings

settings = Settings()

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Langfuse client for traces
langfuse = Langfuse(
    public_key=settings.langfuse_public_key,
    secret_key=settings.langfuse_secret_key,
    host=settings.langfuse_host,
)

# Configure Langfuse OpenAI wrapper
langfuse_openai.api_key = settings.openai_api_key
langfuse_openai.base_url = (
    settings.openai_base_url if hasattr(settings, "openai_base_url") else None
)

# Optional debug mode
langfuse_openai.langfuse_debug = settings.langfuse_debug

# Optional sampling rate (0.0 to 1.0)
langfuse_openai.langfuse_sample_rate = 1.0  # Log all requests

# Verify Langfuse connection in development
if settings.environment != "prod":
    try:
        langfuse_openai.langfuse_auth_check()
        logger.info("Langfuse connection verified")
    except Exception as e:
        logger.error(f"Failed to verify Langfuse connection: {e}")

# Create OpenAI client with Langfuse monitoring
monitored_client = langfuse_openai.AsyncOpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_base_url if hasattr(settings, "openai_base_url") else None,
)


class TraceManager:
    def __init__(self):
        self.traces = {}

    def create_trace(self, patient_id: str) -> str:
        """Create a new trace for a conversation."""
        try:
            trace = langfuse.trace(
                id=f"aria-{patient_id}",
                metadata={
                    "patient_id": patient_id,
                    "environment": settings.environment,
                },
            )
            self.traces[trace.id] = {
                "start_time": time.time(),
                "trace": trace,
            }
            return trace.id
        except Exception as e:
            logger.error(f"Failed to create Langfuse trace: {e}")
            return None

    def end_trace(self, trace_id: str) -> None:
        """End a trace."""
        try:
            if trace_id and trace_id in self.traces:
                trace_data = self.traces[trace_id]
                latency = int((time.time() - trace_data["start_time"]) * 1000)  # ms

                # Create a final span to mark completion
                trace_data["trace"].span(
                    name="completion",
                    start_time=trace_data["start_time"],
                    end_time=time.time(),
                    metadata={
                        "latency_ms": latency,
                    },
                )

                del self.traces[trace_id]
        except Exception as e:
            logger.error(f"Failed to end Langfuse trace: {e}")


# Create global trace manager
trace_manager = TraceManager()


def create_trace(patient_id: str) -> str:
    """Create a new trace for a conversation."""
    return trace_manager.create_trace(patient_id)


def end_trace(trace_id: str) -> None:
    """End a trace."""
    trace_manager.end_trace(trace_id)


def flush_monitoring() -> None:
    """Flush any queued monitoring events."""
    try:
        langfuse_openai.flush_langfuse()
        langfuse.flush()
    except Exception as e:
        logger.error(f"Failed to flush Langfuse events: {e}")


# Export the monitored client and functions
__all__ = ["monitored_client", "create_trace", "end_trace", "flush_monitoring"]
