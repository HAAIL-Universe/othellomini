"""POST /api/v1/chat endpoint for AI chat with consent-gated suggestions."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from backend.schemas.chat import ChatRequest, ChatResponse
from backend.schemas.suggestion import SuggestionResponse
from backend.services.chat_service import ChatService
from backend.services.profile_service import ProfileService
from backend.api.dependencies import get_user_id, get_profile_service, get_chat_service

logger = logging.getLogger(__name__)

# Re-export for interface map compatibility
SuggestionInline = SuggestionResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_suggestion_response(raw: Dict[str, Any]) -> SuggestionResponse:
    """Convert a raw suggestion dict from ChatService to SuggestionResponse."""
    ethical = raw.get("ethical_reasoning", {})
    from backend.schemas.suggestion import EthicalReasoning
    reasoning = EthicalReasoning(
        passed=ethical.get("passed", True),
        justification=ethical.get("justification", ""),
        flags=ethical.get("flags", []),
        confidence=ethical.get("confidence", 0.5),
    )
    from datetime import datetime, timezone
    return SuggestionResponse(
        suggestion_id=raw.get("suggestion_id", raw.get("id", "")),
        text=raw.get("text", raw.get("suggestion_text", "")),
        action_type=raw.get("action_type"),
        consent_tier=raw.get("consent_tier", "Suggestive"),
        ethical_reasoning=reasoning,
        risk_level=raw.get("risk_level", "low"),
        status=raw.get("status", "pending"),
        created_at=raw.get("created_at", datetime.now(timezone.utc)),
        expires_at=raw.get("expires_at"),
        conversation_id=raw.get("conversation_id"),
    )


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user_id: str = Depends(get_user_id),
    profile_service: ProfileService = Depends(get_profile_service),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """Send a chat message and receive AI response with gated suggestions."""
    try:
        context = None
        if request.context:
            context = request.context.model_dump(exclude_none=True)

        result = await chat_service.process_message(
            message=request.message,
            user_id=user_id,
            context=context,
        )

        # Build suggestion responses from raw dicts
        suggestions: List[SuggestionResponse] = []
        for raw_suggestion in result.get("suggestions", []):
            try:
                if isinstance(raw_suggestion, dict):
                    suggestions.append(_build_suggestion_response(raw_suggestion))
                elif isinstance(raw_suggestion, SuggestionResponse):
                    suggestions.append(raw_suggestion)
            except Exception as e:
                logger.warning("Failed to parse suggestion: %s", e)
                continue

        from backend.schemas.chat import ChatMetadata
        metadata = None
        raw_meta = result.get("metadata")
        if isinstance(raw_meta, dict):
            metadata = ChatMetadata(
                ai_model=raw_meta.get("ai_model"),
                tokens_used=raw_meta.get("tokens_used"),
                processing_time_ms=raw_meta.get("processing_time_ms"),
            )

        return ChatResponse(
            conversation_id=result.get("conversation_id", ""),
            message=request.message,
            response=result.get("response", ""),
            suggestions=suggestions,
            profile_updated=result.get("profile_updated", False),
            metadata=metadata,
        )

    except ValueError as exc:
        logger.warning("Invalid chat request for user_id=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Chat processing failed for user_id=%s: %s", user_id, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message.",
        ) from exc
