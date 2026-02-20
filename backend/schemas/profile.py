"""Pydantic schemas for user profile GET response and PATCH request.

Defines request/response models for the /api/v1/profile endpoints including
consent tier validation, traits representation, preferences, and context summary.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ConsentTier(str, Enum):
    """Consent tier levels determining suggestion visibility.

    Hierarchy: passive < suggestive < active < autonomous
    """

    PASSIVE = "passive"
    SUGGESTIVE = "suggestive"
    ACTIVE = "active"
    AUTONOMOUS = "autonomous"


class CommunicationStyle(str, Enum):
    """Supported communication style preferences."""

    DIRECT = "direct"
    GENTLE = "gentle"
    ANALYTICAL = "analytical"
    MOTIVATIONAL = "motivational"


class NotificationFrequency(str, Enum):
    """Supported notification frequency settings."""

    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


class RiskTolerance(str, Enum):
    """Risk tolerance levels for user traits."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionStyle(str, Enum):
    """Decision-making style categories."""

    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    COLLABORATIVE = "collaborative"
    AVOIDANT = "avoidant"


class MoodTrend(str, Enum):
    """Mood trend directions derived from conversation analysis."""

    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


class TraitsSchema(BaseModel):
    """Psychological traits learned from conversations (read-only).

    All numeric scores use 0.0-1.0 scale where 0.0 = low trait expression
    and 1.0 = high trait expression.
    """

    openness: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Openness to new experiences (Big Five trait)",
    )
    conscientiousness: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Conscientiousness trait score",
    )
    extraversion: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Extraversion trait score",
    )
    agreeableness: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Agreeableness trait score",
    )
    neuroticism: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Neuroticism trait score",
    )
    risk_tolerance: Optional[RiskTolerance] = Field(
        None,
        description="Overall risk tolerance level",
    )
    decision_style: Optional[DecisionStyle] = Field(
        None,
        description="Predominant decision-making style",
    )

    model_config = {"from_attributes": True}


class PreferencesSchema(BaseModel):
    """User-defined preferences (editable via PATCH /profile)."""

    communication_style: Optional[CommunicationStyle] = Field(
        None,
        description="Preferred communication style for AI responses",
    )
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Areas of focus for suggestions and guidance",
    )
    notification_frequency: Optional[NotificationFrequency] = Field(
        None,
        description="How frequently to surface suggestions",
    )

    model_config = {"from_attributes": True}


class ContextSummarySchema(BaseModel):
    """Recent context extracted from last N conversations."""

    recent_topics: Optional[List[str]] = Field(
        None,
        description="Top 5 topics from recent conversations",
    )
    mood_trend: Optional[MoodTrend] = Field(
        None,
        description="Trend direction of user mood over recent interactions",
    )
    last_interaction: Optional[datetime] = Field(
        None,
        description="Timestamp of last user interaction",
    )

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    """Response schema for GET /api/v1/profile.

    Returns the full persistent user profile including traits,
    preferences, consent tier, and recent context summary.
    """

    user_id: str = Field(
        ...,
        description="Fixed user identifier (single-user MVP)",
    )
    consent_tier: ConsentTier = Field(
        ...,
        description="Current consent level determining suggestion visibility",
    )
    traits: TraitsSchema = Field(
        default_factory=TraitsSchema,
        description="Psychological traits learned from conversations (read-only)",
    )
    preferences: PreferencesSchema = Field(
        default_factory=PreferencesSchema,
        description="User-defined preferences (editable via PATCH /profile)",
    )
    context_summary: Optional[ContextSummarySchema] = Field(
        None,
        description="Recent context extracted from last N conversations",
    )
    profile_version: int = Field(
        ...,
        description="Profile version number incremented on each update",
    )
    created_at: datetime = Field(
        ...,
        description="Profile creation timestamp",
    )
    updated_at: datetime = Field(
        ...,
        description="Last profile update timestamp",
    )

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    """Request schema for PATCH /api/v1/profile.

    Allows updating consent tier and explicit preferences.
    Trait updates are NOT allowed via this endpoint
    (traits are auto-learned from conversations).
    """

    consent_tier: Optional[ConsentTier] = Field(
        None,
        description="New consent tier level",
    )
    preferences: Optional[PreferencesSchema] = Field(
        None,
        description="Explicit user preferences to update",
    )

    model_config = {"from_attributes": True}


class ProfileClearResponse(BaseModel):
    """Response schema for POST /api/v1/profile/clear.

    Confirms that profile data has been reset to defaults.
    """

    success: bool = Field(
        ...,
        description="Whether the clear operation succeeded",
    )
    message: str = Field(
        ...,
        description="Human-readable status message",
    )
