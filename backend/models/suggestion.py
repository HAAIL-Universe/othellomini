"""SQLAlchemy model for suggestions table.

Stores AI-generated action suggestions with ethical gating metadata,
consent tier assignment, and user approval/denial status tracking.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import relationship

from backend.database import Base


class Suggestion(Base):
    """SQLAlchemy model for the suggestions table.

    Represents an AI-generated action suggestion that has been processed
    through the Othello ethical gatekeeper. Tracks the full lifecycle from
    creation through user approval/denial or expiration.

    Attributes:
        id: Primary key (auto-incrementing integer).
        user_profile_id: Foreign key to user_profiles table.
        conversation_id: Optional foreign key to the conversation that generated this suggestion.
        suggestion_text: Human-readable suggestion presented to the user.
        consent_tier: Othello-assigned consent tier (Passive/Suggestive/Active/Autonomous).
        ethical_reasoning: Othello gatekeeper justification for consent tier assignment.
        status: Current lifecycle state (pending/approved/denied/expired).
        action_type: Category of suggested action (e.g., reflection, scheduling).
        action_payload: Structured data for action execution (JSON).
        user_response: Optional user feedback when approving or denying.
        responded_at: Timestamp when user approved/denied the suggestion.
        created_at: Record creation timestamp.
        updated_at: Record last modification timestamp.
    """

    __tablename__ = "suggestions"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_profile_id: int = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    conversation_id: Optional[int] = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    suggestion_text: str = Column(Text, nullable=False)
    consent_tier: str = Column(
        String(50),
        nullable=False,
        index=True,
    )
    ethical_reasoning: str = Column(Text, nullable=False)
    status: str = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )
    action_type: Optional[str] = Column(String(100), nullable=True)
    action_payload: Optional[dict] = Column(JSON, default=dict, nullable=True)
    user_response: Optional[str] = Column(Text, nullable=True)
    responded_at: Optional[datetime] = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user_profile = relationship("UserProfile", back_populates="suggestions")
    conversation = relationship("Conversation", back_populates="suggestions")

    # Table-level constraints
    __table_args__ = (
        # Consent tier must be one of the valid values
        # SQLite CHECK constraints
        {"comment": "AI-generated action suggestions with ethical gating and user responses"},
    )

    def __repr__(self) -> str:
        return (
            f"<Suggestion(id={self.id}, status='{self.status}', "
            f"consent_tier='{self.consent_tier}', "
            f"action_type='{self.action_type}')>"
        )

    @property
    def is_pending(self) -> bool:
        """Check if the suggestion is still awaiting user action."""
        return self.status == "pending"

    @property
    def is_resolved(self) -> bool:
        """Check if the suggestion has been approved or denied."""
        return self.status in ("approved", "denied")

    @property
    def is_expired(self) -> bool:
        """Check if the suggestion has expired."""
        return self.status == "expired"

    def approve(self, feedback: Optional[str] = None) -> None:
        """Mark the suggestion as approved.

        Args:
            feedback: Optional user feedback explaining the approval.

        Raises:
            ValueError: If the suggestion is not in pending status.
        """
        if self.status != "pending":
            raise ValueError(
                f"Cannot approve suggestion with status '{self.status}'. "
                f"Only pending suggestions can be approved."
            )
        self.status = "approved"
        self.user_response = feedback
        self.responded_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def deny(self, reason: Optional[str] = None) -> None:
        """Mark the suggestion as denied.

        Args:
            reason: Optional user reason for denial.

        Raises:
            ValueError: If the suggestion is not in pending status.
        """
        if self.status != "pending":
            raise ValueError(
                f"Cannot deny suggestion with status '{self.status}'. "
                f"Only pending suggestions can be denied."
            )
        self.status = "denied"
        self.user_response = reason
        self.responded_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def expire(self) -> None:
        """Mark the suggestion as expired.

        Raises:
            ValueError: If the suggestion is not in pending status.
        """
        if self.status != "pending":
            raise ValueError(
                f"Cannot expire suggestion with status '{self.status}'. "
                f"Only pending suggestions can be expired."
            )
        self.status = "expired"
        self.updated_at = datetime.now(timezone.utc)


# Valid values for constraint enforcement at the application level
VALID_CONSENT_TIERS = ("Passive", "Suggestive", "Active", "Autonomous")
VALID_STATUSES = ("pending", "approved", "denied", "expired")
VALID_ACTION_TYPES = (
    "reflection",
    "scheduling",
    "communication",
    "research",
    "habit",
    "goal",
)
