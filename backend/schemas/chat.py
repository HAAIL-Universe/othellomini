"""Pydantic request/response models for the /chat endpoint.

Defines request validation and response serialization for chat interactions,
including message input, optional context, AI response, and consent-gated suggestions.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from backend.schemas.suggestion import SuggestionResponse


class ChatContext(BaseModel):
    """Optional contextual metadata accompanying a chat message."""

    mood: Optional[str] = Field(
        None,
        description="User's current mood state",
        pattern="^(calm|stressed|happy|sad|neutral)$",
    )
    timestamp: Optional[datetime] = Field(
        None,
        description="ISO 8601 timestamp for the message (defaults to server time if omitted)",
    )


class ChatRequest(BaseModel):
    """Request body for POST /api/v1/chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's chat message text",
        examples=["I've been feeling overwhelmed with work lately. Any advice?"],
    )
    context: Optional[ChatContext] = Field(
        None,
        description="Optional additional context (mood, timestamp)",
    )


class ChatMetadata(BaseModel):
    """Metadata about the AI response generation."""

    ai_model: Optional[str] = Field(
        None,
        description="OpenAI model used for generation",
        examples=["gpt-4"],
    )
    tokens_used: Optional[int] = Field(
        None,
        description="Total tokens consumed in the API call",
        examples=[342],
    )
    processing_time_ms: Optional[int] = Field(
        None,
        description="Total processing time in milliseconds",
        examples=[1820],
    )


class ChatResponse(BaseModel):
    """Response body for POST /api/v1/chat endpoint."""

    conversation_id: str = Field(
        ...,
        description="Unique identifier for this conversation turn",
        examples=["c7f8a3e1-4b2d-4f9a-8c3e-1a2b3c4d5e6f"],
    )
    message: str = Field(
        ...,
        description="Echo of user's original message",
        examples=["I've been feeling overwhelmed with work lately. Any advice?"],
    )
    response: str = Field(
        ...,
        description="AI-generated conversational response",
        examples=[
            "It sounds like you're carrying a heavy load right now. "
            "Taking short breaks can help reset your focus. "
            "Would you like me to suggest a few specific strategies?"
        ],
    )
    suggestions: list[SuggestionResponse] = Field(
        default_factory=list,
        description="List of consent-gated action suggestions",
    )
    profile_updated: bool = Field(
        ...,
        description="Indicates if user profile was updated from this interaction",
        examples=[True],
    )
    metadata: Optional[ChatMetadata] = Field(
        None,
        description="Additional conversation metadata",
    )
