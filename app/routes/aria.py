from fastapi import APIRouter, HTTPException
from typing import Dict
from app.core.agent import aria
from app.core.memory import memory
from app.models.schema import (
    AriaRequest,
    AriaResponse,
    ReformulationRequest,
    ContentViolationError,
)
from app.core.moderation import moderator

router = APIRouter()


@router.post(
    "/patient/chat",
    response_model=AriaResponse,
    responses={403: {"model": ContentViolationError}},
)
async def chat_with_aria(request: AriaRequest):
    """
    Chat with ARIA, the maternal health expert.

    This endpoint:
    1. Retrieves recent conversation history from DynamoDB
    2. Processes the message using the ReAct agent
    3. Returns ARIA's response along with information about tools used
    """
    try:
        # Check content moderation
        is_violation = await moderator.moderate_content(request.message)
        if is_violation:
            raise HTTPException(status_code=403, detail=ContentViolationError().error)

        # Get recent conversation history
        recent_history = await memory.get_recent_interactions(
            patient_id=request.patient_id, limit=request.history_limit
        )

        # Process message through ARIA agent
        result = await aria.process_message(
            patient_id=request.patient_id,
            message=request.message,
            recent_history=recent_history,
        )

        return AriaResponse(
            response=result["response"], tools_used=result["tools_used"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/patient/reformulate",
    response_model=AriaResponse,
    responses={403: {"model": ContentViolationError}},
)
async def reformulate_response(request: ReformulationRequest):
    """
    Reformulate a previous response from ARIA.

    This endpoint:
    1. Takes a previous response and reformulation parameters
    2. Uses ARIA to provide a new version of the response
    3. Supports elaboration, simplification, and clarification
    """
    try:
        # Check content moderation
        is_violation = await moderator.moderate_content(request.original_response)
        if is_violation:
            raise HTTPException(status_code=403, detail=ContentViolationError().error)

        result = await aria.reformulate_response(
            patient_id=request.patient_id,
            original_response=request.original_response,
            reformulation_type=request.reformulation_type,
            specific_focus=request.specific_focus,
        )

        return AriaResponse(
            response=result["response"], tools_used=result["tools_used"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/patient/history/{patient_id}")
async def clear_chat_history(patient_id: str):
    """Clear conversation history for a specific patient."""
    try:
        await memory.clear_patient_history(patient_id)
        return {"status": "success", "message": "Chat history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
