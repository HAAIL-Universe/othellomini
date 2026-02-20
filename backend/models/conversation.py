"""SQLAlchemy model for the conversations table.

Stores chat message log with user/assistant/system roles. Provides conversation
history for context reconstruction and audit trail.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint,
)
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from backend.database import Base


class Conversation(Base):
    """Represents a single chat message in a conversation thread.

    Each row stores one message (user, assistant, or system role) linked to a
    user profile. Messages are ordered by created_at timestamp to reconstruct
    conversation flow.

    Attributes:
        id: Auto-incrementing primary key.
        user_profile_id: Foreign key referencing user_profiles.id.
        role: Message author role - 'user', 'assistant', or 'system'.
        content: Full message text content.
        metadata_: Optional JSON metadata (token count, model version, processing time).
        created_at: Timestamp when the message was created.
        updated_at: Timestamp when the record was last modified.
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_profile_id = Column(
        Integer,
        ForeignKey("user_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(
        String(50),
        nullable=False,
    )
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict, nullable=True)
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
    user_profile = relationship("UserProfile", back_populates="conversations")
    suggestions = relationship(
        "Suggestion",
        back_populates="conversation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="role_check",
        ),
        Index("idx_conversations_created_at", created_at.desc()),
        Index("idx_conversations_role", "role"),
    )

    def __repr__(self) -> str:
        return (
            f"<Conversation(id={self.id}, user_profile_id={self.user_profile_id}, "
            f"role='{self.role}', created_at={self.created_at})>"
        )
