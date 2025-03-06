from pydantic import BaseModel
from typing import List, Optional, Dict


class QueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    collection_name: Optional[str] = None


class Source(BaseModel):
    metadata: Dict[str, str]
    distance: float
    text: str


class QueryResponse(BaseModel):
    answer: str
    sources: Optional[List[Source]] = None


class DocumentInput(BaseModel):
    urls: List[str]
    collection_name: Optional[str] = None


class AriaRequest(BaseModel):
    """Request model for ARIA endpoint."""

    patient_id: str
    message: str
    history_limit: Optional[int] = 5


class AriaResponse(BaseModel):
    """Response model for ARIA endpoint."""

    response: str
    tools_used: List[str]


class ReformulationRequest(BaseModel):
    """Request model for response reformulation."""

    patient_id: str
    original_response: str
    reformulation_type: str = "elaborate"  # elaborate, simplify, or clarify
    specific_focus: Optional[str] = None  # Optional specific aspect to focus on


class ContentViolationError(BaseModel):
    """Response model for content policy violations."""

    error: str = "Text was found that violates The Journey Pregnancy content policy."
    details: Optional[str] = None
