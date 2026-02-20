"""SQLAlchemy model for the user_profiles table.

Stores persistent user model including psychological traits, preferences,
behavioral patterns, and consent tier settings. Single-user scope for MVP.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.database import Base

try:
    from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
    JSONType = SQLiteJSON
except ImportError:
    from sqlalchemy import JSON as JSONType


class UserProfile(Base):
    """SQLAlchemy model representing the user_profiles table.

    Stores persistent user psychological model and consent settings.
    For MVP, only a single row is expected (single-user scope).

    Attributes:
        id: Primary key (auto-incrementing integer).
        user_id: Unique identifier for user (fixed for single-user MVP).
        display_name: Optional human-readable display name.
        consent_tier: Current consent level determining suggestion visibility.
            One of: Passive, Suggestive, Active, Autonomous.
        traits: JSON object storing psychological traits
            (e.g., {"openness": 0.8, "conscientiousness": 0.7}).
        preferences: JSON object storing user preferences
            (e.g., {"communication_style": "direct", "priority_areas": ["health"]}).
        behavioral_patterns: JSON object storing observed behavioral patterns
            (e.g., {"morning_routine": "exercise", "work_hours": "9-17"}).
        context_summary: Narrative summary of current user context for AI reference.
        profile_version: Incremented on each update for auditability.
        created_at: Record creation timestamp (UTC).
        updated_at: Record last modification timestamp (UTC).
    """

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, unique=True, index=True)
    display_name = Column(String(255), nullable=True)
    consent_tier = Column(
        String(50),
        nullable=False,
        default="Passive",
    )
    traits = Column(JSONType, nullable=False, default=dict)
    preferences = Column(JSONType, nullable=False, default=dict)
    behavioral_patterns = Column(JSONType, nullable=False, default=dict)
    context_summary = Column(Text, nullable=True)
    profile_version = Column(Integer, nullable=False, default=1)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    conversations = relationship(
        "Conversation",
        back_populates="user_profile",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    suggestions = relationship(
        "Suggestion",
        back_populates="user_profile",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    __table_args__ = (
        CheckConstraint(
            "consent_tier IN ('Passive', 'Suggestive', 'Active', 'Autonomous')",
            name="consent_tier_check",
        ),
        UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
        {"comment": "Persistent user psychological model and consent settings"},
    )

    def __repr__(self) -> str:
        return (
            f"<UserProfile(id={self.id}, user_id='{self.user_id}', "
            f"consent_tier='{self.consent_tier}', version={self.profile_version})>"
        )

    def increment_version(self) -> None:
        """Increment the profile version for auditability.

        Should be called before committing any profile update.
        """
        self.profile_version = (self.profile_version or 0) + 1
        self.updated_at = datetime.now(timezone.utc)
