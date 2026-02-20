"""
ConversationRepository for conversations table operations.

Provides data access methods for creating conversation messages, listing
conversation history by user profile, and retrieving individual messages.
All ORM/SQL logic is encapsulated within this repository layer.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.conversation import Conversation
from backend.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """
    Repository for managing conversation records in the conversations table.

    Provides operations for creating chat messages, retrieving conversation
    history filtered by user profile, and paginated listing with ordering
    by creation timestamp.

    Inherits common CRUD operations from BaseRepository.
    """

    model = Conversation

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the ConversationRepository with an async database session.

        Args:
            session: SQLAlchemy AsyncSession instance for database operations.
        """
        super().__init__(session)

    async def create_message(
        self,
        user_profile_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Conversation:
        """
        Create a new conversation message record.

        Args:
            user_profile_id: The ID of the user profile this message belongs to.
            role: The message role - one of 'user', 'assistant', or 'system'.
            content: The text content of the message.
            metadata: Optional JSON metadata (e.g., mood, context, timestamps).

        Returns:
            The newly created Conversation instance.
        """
        data: Dict[str, Any] = {
            "user_profile_id": user_profile_id,
            "role": role,
            "content": content,
            "metadata": metadata if metadata is not None else {},
        }
        return await self.create(data)

    async def get_by_user_profile_id(
        self,
        user_profile_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Conversation]:
        """
        Retrieve conversation messages for a specific user profile, ordered by
        creation time ascending (oldest first).

        Args:
            user_profile_id: The ID of the user profile to filter by.
            offset: Number of records to skip (default 0).
            limit: Maximum number of records to return (default 100).

        Returns:
            List of Conversation instances ordered by created_at ascending.
        """
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_profile_id == user_profile_id)
            .order_by(Conversation.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_recent_by_user_profile_id(
        self,
        user_profile_id: int,
        limit: int = 20,
    ) -> List[Conversation]:
        """
        Retrieve the most recent conversation messages for a user profile,
        returned in chronological order (oldest first within the window).

        This is useful for building context windows for AI prompts.

        Args:
            user_profile_id: The ID of the user profile to filter by.
            limit: Maximum number of recent messages to retrieve (default 20).

        Returns:
            List of Conversation instances, chronologically ordered.
        """
        # Subquery to get the most recent messages by descending order
        subquery = (
            select(Conversation)
            .where(Conversation.user_profile_id == user_profile_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .subquery()
        )

        # Re-select from subquery and order ascending for chronological context
        from sqlalchemy.orm import aliased
        conv_alias = aliased(Conversation, subquery)
        result = await self.session.execute(
            select(conv_alias).order_by(subquery.c.created_at.asc())
        )
        return list(result.scalars().all())

    async def get_by_role(
        self,
        user_profile_id: int,
        role: str,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Conversation]:
        """
        Retrieve conversation messages filtered by user profile and role.

        Args:
            user_profile_id: The ID of the user profile to filter by.
            role: The message role to filter by ('user', 'assistant', 'system').
            offset: Number of records to skip (default 0).
            limit: Maximum number of records to return (default 100).

        Returns:
            List of Conversation instances matching the role filter.
        """
        result = await self.session.execute(
            select(Conversation)
            .where(
                Conversation.user_profile_id == user_profile_id,
                Conversation.role == role,
            )
            .order_by(Conversation.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_user_profile_id(self, user_profile_id: int) -> int:
        """
        Count total conversation messages for a specific user profile.

        Args:
            user_profile_id: The ID of the user profile to count messages for.

        Returns:
            Integer count of conversation messages.
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(Conversation)
            .where(Conversation.user_profile_id == user_profile_id)
        )
        return result.scalar() or 0

    async def delete_by_user_profile_id(self, user_profile_id: int) -> int:
        """
        Delete all conversation messages for a specific user profile.

        Useful for clearing conversation history when user requests data deletion.

        Args:
            user_profile_id: The ID of the user profile whose messages to delete.

        Returns:
            Number of records deleted.
        """
        from sqlalchemy import delete as sql_delete

        result = await self.session.execute(
            sql_delete(Conversation).where(
                Conversation.user_profile_id == user_profile_id
            )
        )
        await self.session.flush()
        return result.rowcount
