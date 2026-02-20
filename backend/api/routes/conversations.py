"""Conversation history endpoints."""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

from backend.repositories.conversation_repository import ConversationRepository
from backend.repositories.profile_repository import ProfileRepository
from backend.api.dependencies import (
    get_user_id,
    get_conversation_repo_with_session,
    get_profile_repo_with_session,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationMessage(BaseModel):
    """Single conversation message."""

    id: int
    role: str
    content: str
    metadata: Optional[dict] = None
    created_at: datetime


class ConversationDetailResponse(BaseModel):
    """Detail response for a single conversation message."""

    id: int
    user_profile_id: int
    role: str
    content: str
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    """Paginated list of conversation messages."""

    conversations: List[ConversationMessage]
    total: int
    limit: int
    offset: int


def _message_to_schema(msg) -> ConversationMessage:
    """Convert a Conversation ORM instance to ConversationMessage."""
    return ConversationMessage(
        id=msg.id,
        role=msg.role,
        content=msg.content,
        metadata=msg.metadata_,
        created_at=msg.created_at,
    )


def _message_to_detail(msg) -> ConversationDetailResponse:
    """Convert a Conversation ORM instance to ConversationDetailResponse."""
    return ConversationDetailResponse(
        id=msg.id,
        user_profile_id=msg.user_profile_id,
        role=msg.role,
        content=msg.content,
        metadata=msg.metadata_,
        created_at=msg.created_at,
        updated_at=msg.updated_at,
    )


@router.get("", response_model=ConversationListResponse)
async def list_conversations(
    user_id: str = Depends(get_user_id),
    limit: int = Query(default=50, ge=1, le=200, description="Max messages to return"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    repo: ConversationRepository = Depends(get_conversation_repo_with_session),
    profile_repo: ProfileRepository = Depends(get_profile_repo_with_session),
) -> ConversationListResponse:
    """List conversation messages for the current user with pagination."""
    try:
        profile = await profile_repo.get_by_user_id(user_id)
        if profile is None:
            return ConversationListResponse(
                conversations=[], total=0, limit=limit, offset=offset
            )

        messages = await repo.get_by_user_profile_id(
            user_profile_id=profile.id, offset=offset, limit=limit
        )
        total = await repo.count_by_user_profile_id(user_profile_id=profile.id)

        return ConversationListResponse(
            conversations=[_message_to_schema(m) for m in messages],
            total=total,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:
        logger.error("Failed to list conversations for user_id=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history.",
        ) from exc


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: int = Path(..., description="Conversation message ID"),
    user_id: str = Depends(get_user_id),
    repo: ConversationRepository = Depends(get_conversation_repo_with_session),
    profile_repo: ProfileRepository = Depends(get_profile_repo_with_session),
) -> ConversationDetailResponse:
    """Retrieve a single conversation message by ID."""
    try:
        profile = await profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found.",
            )

        message = await repo.get_by_id(conversation_id)
        if message is None or message.user_profile_id != profile.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation message {conversation_id} not found.",
            )

        return _message_to_detail(message)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            "Failed to get conversation %s for user_id=%s: %s",
            conversation_id, user_id, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation message.",
        ) from exc
