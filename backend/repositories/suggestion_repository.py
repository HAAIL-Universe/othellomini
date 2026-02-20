"""
SuggestionRepository for suggestions table operations.

Provides data access methods for creating suggestions, updating their status
(approve/deny), listing pending suggestions, and querying by various criteria.
This repository encapsulates all ORM/SQL logic for the suggestions table —
services interact via this interface only.
"""

from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.suggestion import Suggestion
from backend.repositories.base import BaseRepository


class SuggestionRepository(BaseRepository[Suggestion]):
    """
    Repository for managing suggestion records in the database.

    Handles CRUD operations for AI-generated suggestions including creation,
    status updates (pending → approved/denied), filtering by status and
    consent tier, and retrieval by user profile association.

    Attributes:
        model: The Suggestion SQLAlchemy model class.
        session: The async database session for executing queries.
    """

    model = Suggestion

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the SuggestionRepository with an async database session.

        Args:
            session: SQLAlchemy AsyncSession instance for database operations.
        """
        super().__init__(session)

    async def create_suggestion(self, data: dict[str, Any]) -> Suggestion:
        """
        Create a new suggestion record.

        Args:
            data: Dictionary containing suggestion fields. Expected keys:
                - user_profile_id (int): Foreign key to user_profiles table.
                - conversation_id (int, optional): Foreign key to conversations table.
                - suggestion_text (str): AI-generated action description.
                - consent_tier (str): Required consent tier (Passive/Suggestive/Active/Autonomous).
                - ethical_reasoning (str): Othello gatekeeper justification.
                - status (str, optional): Initial status (defaults to 'pending').
                - metadata (dict, optional): Additional structured data.

        Returns:
            The newly created Suggestion instance with generated fields populated.
        """
        if "status" not in data:
            data["status"] = "pending"
        return await self.create(data)

    async def get_by_user_profile_id(
        self,
        user_profile_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Suggestion]:
        """
        Retrieve all suggestions for a specific user profile.

        Args:
            user_profile_id: The user profile ID to filter by.
            offset: Number of records to skip (default 0).
            limit: Maximum number of records to return (default 100).

        Returns:
            List of Suggestion instances ordered by creation time descending.
        """
        result = await self.session.execute(
            select(Suggestion)
            .where(Suggestion.user_profile_id == user_profile_id)
            .order_by(Suggestion.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending(
        self,
        user_profile_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Suggestion]:
        """
        Retrieve all pending suggestions for a specific user profile.

        Args:
            user_profile_id: The user profile ID to filter by.
            offset: Number of records to skip (default 0).
            limit: Maximum number of records to return (default 100).

        Returns:
            List of pending Suggestion instances ordered by creation time descending.
        """
        result = await self.session.execute(
            select(Suggestion)
            .where(
                and_(
                    Suggestion.user_profile_id == user_profile_id,
                    Suggestion.status == "pending",
                )
            )
            .order_by(Suggestion.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_status(
        self,
        status: str,
        user_profile_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Suggestion]:
        """
        Retrieve suggestions filtered by status, optionally scoped to a user profile.

        Args:
            status: The status to filter by ('pending', 'approved', 'denied').
            user_profile_id: Optional user profile ID to scope the query.
            offset: Number of records to skip (default 0).
            limit: Maximum number of records to return (default 100).

        Returns:
            List of matching Suggestion instances ordered by creation time descending.
        """
        conditions = [Suggestion.status == status]
        if user_profile_id is not None:
            conditions.append(Suggestion.user_profile_id == user_profile_id)

        result = await self.session.execute(
            select(Suggestion)
            .where(and_(*conditions))
            .order_by(Suggestion.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_consent_tier(
        self,
        consent_tier: str,
        user_profile_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Suggestion]:
        """
        Retrieve suggestions filtered by consent tier, optionally scoped to a user profile.

        Args:
            consent_tier: The consent tier to filter by
                ('Passive', 'Suggestive', 'Active', 'Autonomous').
            user_profile_id: Optional user profile ID to scope the query.
            offset: Number of records to skip (default 0).
            limit: Maximum number of records to return (default 100).

        Returns:
            List of matching Suggestion instances ordered by creation time descending.
        """
        conditions = [Suggestion.consent_tier == consent_tier]
        if user_profile_id is not None:
            conditions.append(Suggestion.user_profile_id == user_profile_id)

        result = await self.session.execute(
            select(Suggestion)
            .where(and_(*conditions))
            .order_by(Suggestion.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_conversation_id(
        self,
        conversation_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Suggestion]:
        """
        Retrieve all suggestions associated with a specific conversation.

        Args:
            conversation_id: The conversation ID to filter by.
            offset: Number of records to skip (default 0).
            limit: Maximum number of records to return (default 100).

        Returns:
            List of Suggestion instances for the given conversation.
        """
        result = await self.session.execute(
            select(Suggestion)
            .where(Suggestion.conversation_id == conversation_id)
            .order_by(Suggestion.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def approve(self, suggestion_id: int) -> Optional[Suggestion]:
        """
        Mark a suggestion as approved and set the resolved timestamp.

        Updates the suggestion status from 'pending' to 'approved' and records
        the resolution time. Only pending suggestions can be approved.

        Args:
            suggestion_id: The primary key ID of the suggestion to approve.

        Returns:
            The updated Suggestion instance if found and was pending, None otherwise.
        """
        suggestion = await self.get_by_id(suggestion_id)
        if suggestion is None:
            return None

        if suggestion.status != "pending":
            return suggestion

        now = datetime.now(timezone.utc)
        return await self.update_by_id(
            suggestion_id,
            {
                "status": "approved",
                "resolved_at": now,
                "updated_at": now,
            },
        )

    async def deny(self, suggestion_id: int) -> Optional[Suggestion]:
        """
        Mark a suggestion as denied and set the resolved timestamp.

        Updates the suggestion status from 'pending' to 'denied' and records
        the resolution time. Only pending suggestions can be denied.

        Args:
            suggestion_id: The primary key ID of the suggestion to deny.

        Returns:
            The updated Suggestion instance if found and was pending, None otherwise.
        """
        suggestion = await self.get_by_id(suggestion_id)
        if suggestion is None:
            return None

        if suggestion.status != "pending":
            return suggestion

        now = datetime.now(timezone.utc)
        return await self.update_by_id(
            suggestion_id,
            {
                "status": "denied",
                "resolved_at": now,
                "updated_at": now,
            },
        )

    async def update_status(
        self,
        suggestion_id: int,
        status: str,
    ) -> Optional[Suggestion]:
        """
        Update the status of a suggestion to an arbitrary value.

        This is a lower-level method; prefer approve() or deny() for standard
        status transitions.

        Args:
            suggestion_id: The primary key ID of the suggestion to update.
            status: The new status value ('pending', 'approved', 'denied').

        Returns:
            The updated Suggestion instance if found, None otherwise.
        """
        now = datetime.now(timezone.utc)
        update_data: dict[str, Any] = {
            "status": status,
            "updated_at": now,
        }
        if status in ("approved", "denied"):
            update_data["resolved_at"] = now

        return await self.update_by_id(suggestion_id, update_data)

    async def count_pending(self, user_profile_id: int) -> int:
        """
        Count the number of pending suggestions for a user profile.

        Args:
            user_profile_id: The user profile ID to count pending suggestions for.

        Returns:
            Integer count of pending suggestions.
        """
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count())
            .select_from(Suggestion)
            .where(
                and_(
                    Suggestion.user_profile_id == user_profile_id,
                    Suggestion.status == "pending",
                )
            )
        )
        return result.scalar() or 0

    async def delete_by_user_profile_id(self, user_profile_id: int) -> int:
        """
        Delete all suggestions for a specific user profile.

        Args:
            user_profile_id: The user profile ID whose suggestions to delete.

        Returns:
            Number of records deleted.
        """
        from sqlalchemy import delete as sql_delete

        result = await self.session.execute(
            sql_delete(Suggestion).where(
                Suggestion.user_profile_id == user_profile_id
            )
        )
        await self.session.flush()
        return result.rowcount
