"""Initial schema: user_profiles, conversations, suggestions.

Revision ID: 001
Revises: None
Create Date: 2024-01-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_profiles, conversations, and suggestions tables."""
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("consent_tier", sa.String(50), nullable=False, server_default="Passive"),
        sa.Column("traits", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("preferences", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("behavioral_patterns", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("context_summary", sa.Text(), nullable=True),
        sa.Column("profile_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "consent_tier IN ('Passive', 'Suggestive', 'Active', 'Autonomous')",
            name="consent_tier_check",
        ),
        sa.UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
        comment="Persistent user psychological model and consent settings",
    )
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"], unique=True)

    op.create_table(
        "conversations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_profile_id", sa.Integer(), sa.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=True, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="role_check",
        ),
    )
    op.create_index("ix_conversations_user_profile_id", "conversations", ["user_profile_id"])
    op.create_index("idx_conversations_created_at", "conversations", [sa.text("created_at DESC")])
    op.create_index("idx_conversations_role", "conversations", ["role"])

    op.create_table(
        "suggestions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_profile_id", sa.Integer(), sa.ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conversation_id", sa.Integer(), sa.ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("suggestion_text", sa.Text(), nullable=False),
        sa.Column("consent_tier", sa.String(50), nullable=False),
        sa.Column("ethical_reasoning", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("action_type", sa.String(100), nullable=True),
        sa.Column("action_payload", sa.JSON(), nullable=True, server_default="{}"),
        sa.Column("user_response", sa.Text(), nullable=True),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        comment="AI-generated action suggestions with ethical gating and user responses",
    )
    op.create_index("ix_suggestions_user_profile_id", "suggestions", ["user_profile_id"])
    op.create_index("ix_suggestions_conversation_id", "suggestions", ["conversation_id"])
    op.create_index("ix_suggestions_consent_tier", "suggestions", ["consent_tier"])
    op.create_index("ix_suggestions_status", "suggestions", ["status"])
    op.create_index("ix_suggestions_created_at", "suggestions", ["created_at"])


def downgrade() -> None:
    """Drop suggestions, conversations, and user_profiles tables."""
    op.drop_table("suggestions")
    op.drop_table("conversations")
    op.drop_table("user_profiles")
