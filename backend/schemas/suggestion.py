"""Pydantic schemas for suggestion-related request/response models.

Defines models for suggestion listing, approval, denial, and ethical reasoning
display as specified in the physics contract.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EthicalReasoning(BaseModel):
    """Othello's ethical validation details for a suggestion."""

    passed: bool = Field(
        ...,
        description="Whether suggestion passed ethical gate",
    )
    justification: str = Field(
        ...,
        description="Human-readable explanation of ethical assessment",
    )
    flags: List[str] = Field(
        default_factory=list,
        description="Any ethical flags raised (even if suggestion passed)",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Othello's confidence in ethical assessment",
    )


class SuggestionResponse(BaseModel):
    """Response model for a single suggestion with ethical reasoning."""

    suggestion_id: str = Field(
        ...,
        description="Unique suggestion identifier",
    )
    text: str = Field(
        ...,
        description="Human-readable suggestion text",
    )
    action_type: Optional[str] = Field(
        default=None,
        description="Category of suggested action",
    )
    consent_tier: str = Field(
        ...,
        description="Minimum consent tier required for this suggestion",
    )
    ethical_reasoning: EthicalReasoning = Field(
        ...,
        description="Othello's ethical validation details",
    )
    risk_level: str = Field(
        default="low",
        description="Estimated risk level of executing this suggestion",
    )
    status: str = Field(
        default="pending",
        description="Current suggestion status",
    )
    created_at: datetime = Field(
        ...,
        description="When suggestion was generated",
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="When suggestion expires if not acted upon",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Associated conversation that generated this suggestion",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "suggestion_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "text": "Schedule a 15-minute break at 3pm to step outside and reset",
                    "action_type": "scheduling",
                    "consent_tier": "suggestive",
                    "ethical_reasoning": {
                        "passed": True,
                        "justification": "Low-risk self-care suggestion aligned with user's stated goal of reducing stress. No external commitments or data sharing involved.",
                        "flags": [],
                        "confidence": 0.94,
                    },
                    "risk_level": "low",
                    "status": "pending",
                    "created_at": "2024-01-15T14:32:10Z",
                    "expires_at": "2024-01-16T14:32:10Z",
                    "conversation_id": "c7f8a3e1-4b2d-4f9a-8c3e-1a2b3c4d5e6f",
                }
            ]
        }
    }


class SuggestionListResponse(BaseModel):
    """Paginated list of suggestions."""

    suggestions: List[SuggestionResponse] = Field(
        default_factory=list,
        description="List of suggestions matching filter criteria",
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total count of suggestions matching filter",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of suggestions returned",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset",
    )


class SuggestionApproveRequest(BaseModel):
    """Request model for approving a suggestion."""

    feedback: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional user feedback on why this was approved",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "feedback": "This is exactly what I needed right now",
                }
            ]
        }
    }


class SuggestionApproveResponse(BaseModel):
    """Response model after approving a suggestion."""

    suggestion_id: str = Field(
        ...,
        description="Unique suggestion identifier",
    )
    status: str = Field(
        default="approved",
        description="Updated suggestion status",
    )
    approved_at: datetime = Field(
        ...,
        description="Timestamp when suggestion was approved",
    )
    message: str = Field(
        default="Suggestion approved successfully",
        description="Confirmation message",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "suggestion_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "status": "approved",
                    "approved_at": "2024-01-15T14:45:30Z",
                    "message": "Suggestion approved successfully",
                }
            ]
        }
    }


class SuggestionDenyRequest(BaseModel):
    """Request model for denying a suggestion."""

    reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Optional user reason for denial (helps train filter)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "reason": "Too aggressive for my current state",
                }
            ]
        }
    }


class SuggestionDenyResponse(BaseModel):
    """Response model after denying a suggestion."""

    suggestion_id: str = Field(
        ...,
        description="Unique suggestion identifier",
    )
    status: str = Field(
        default="denied",
        description="Updated suggestion status",
    )
    denied_at: datetime = Field(
        ...,
        description="Timestamp when suggestion was denied",
    )
    message: str = Field(
        default="Suggestion denied successfully",
        description="Confirmation message",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "suggestion_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                    "status": "denied",
                    "denied_at": "2024-01-15T14:47:12Z",
                    "message": "Suggestion denied successfully",
                }
            ]
        }
    }


class SuggestionListParams(BaseModel):
    """Query parameters for listing suggestions."""

    status: Optional[str] = Field(
        default="pending",
        description="Filter by suggestion status",
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of suggestions to return",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset",
    )
