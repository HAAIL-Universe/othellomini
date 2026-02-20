"""
ProfileRepository for user_profiles table operations.

Provides specialized data access methods for the user_profiles table including
get by user_id, update profile fields, upsert (create or update), consent tier
management, and profile versioning. Extends BaseRepository for common CRUD.

This repository encapsulates all SQL/ORM logic for user profile persistence.
Services interact exclusively through this interface — no direct database
access from upper layers.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user_profile import UserProfile
from backend.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[UserProfile]):
    """
    Repository for user_profiles table operations.

    Provides CRUD operations specialized for the UserProfile model,
    including lookup by user_id, profile upsert with version incrementing,
    consent tier updates, and trait/preference management.

    Attributes:
        model: The UserProfile SQLAlchemy model class.
        session: The async database session for executing queries.
    """

    model = UserProfile

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the ProfileRepository with an async database session.

        Args:
            session: SQLAlchemy AsyncSession instance for database operations.
        """
        super().__init__(session)

    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        """
        Retrieve a user profile by its unique user_id string.

        This is the primary lookup method for the single-user MVP,
        where user_id is a fixed identifier.

        Args:
            user_id: The unique string identifier for the user.

        Returns:
            The UserProfile instance if found, None otherwise.
        """
        result = await self.session.execute(
            select(self.model).where(self.model.user_id == user_id)
        )
        return result.scalars().first()

    async def upsert(self, user_id: str, data: Dict[str, Any]) -> UserProfile:
        """
        Create or update a user profile by user_id.

        If a profile with the given user_id exists, updates it with the
        provided data and increments the profile_version. If no profile
        exists, creates a new one with the given data.

        Args:
            user_id: The unique string identifier for the user.
            data: Dictionary of field values to set on the profile.
                  May include: display_name, consent_tier, traits,
                  preferences, behavioral_patterns, context_summary.

        Returns:
            The created or updated UserProfile instance.
        """
        existing = await self.get_by_user_id(user_id)

        if existing is not None:
            # Increment profile version for auditability
            update_data = {**data}
            update_data["profile_version"] = existing.profile_version + 1
            update_data["updated_at"] = datetime.now(timezone.utc)

            await self.session.execute(
                update(self.model)
                .where(self.model.id == existing.id)
                .values(**update_data)
            )
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        else:
            # Create new profile
            create_data = {"user_id": user_id, **data}
            return await self.create(create_data)

    async def update_consent_tier(
        self, user_id: str, consent_tier: str
    ) -> Optional[UserProfile]:
        """
        Update the consent tier for a user profile.

        Increments profile_version and updates the updated_at timestamp
        for auditability of consent tier changes.

        Args:
            user_id: The unique string identifier for the user.
            consent_tier: The new consent tier value. Must be one of:
                          'Passive', 'Suggestive', 'Active', 'Autonomous'.

        Returns:
            The updated UserProfile instance if found, None if no profile
            exists for the given user_id.

        Raises:
            ValueError: If consent_tier is not a valid tier value.
        """
        valid_tiers = {"Passive", "Suggestive", "Active", "Autonomous"}
        if consent_tier not in valid_tiers:
            raise ValueError(
                f"Invalid consent tier '{consent_tier}'. "
                f"Must be one of: {', '.join(sorted(valid_tiers))}"
            )

        existing = await self.get_by_user_id(user_id)
        if existing is None:
            return None

        await self.session.execute(
            update(self.model)
            .where(self.model.id == existing.id)
            .values(
                consent_tier=consent_tier,
                profile_version=existing.profile_version + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def update_traits(
        self, user_id: str, traits: Dict[str, Any]
    ) -> Optional[UserProfile]:
        """
        Update the psychological traits for a user profile.

        Merges the provided traits with existing traits (shallow merge),
        increments profile_version, and updates the timestamp.

        Args:
            user_id: The unique string identifier for the user.
            traits: Dictionary of trait key-value pairs to merge into
                    the existing traits. Example:
                    {"openness": 0.8, "conscientiousness": 0.7}

        Returns:
            The updated UserProfile instance if found, None if no profile
            exists for the given user_id.
        """
        existing = await self.get_by_user_id(user_id)
        if existing is None:
            return None

        # Merge existing traits with new traits (new values override)
        current_traits = existing.traits or {}
        merged_traits = {**current_traits, **traits}

        await self.session.execute(
            update(self.model)
            .where(self.model.id == existing.id)
            .values(
                traits=merged_traits,
                profile_version=existing.profile_version + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def update_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> Optional[UserProfile]:
        """
        Update the user preferences for a user profile.

        Merges the provided preferences with existing preferences (shallow merge),
        increments profile_version, and updates the timestamp.

        Args:
            user_id: The unique string identifier for the user.
            preferences: Dictionary of preference key-value pairs to merge.
                         Example: {"communication_style": "direct",
                                   "priority_areas": ["health"]}

        Returns:
            The updated UserProfile instance if found, None if no profile
            exists for the given user_id.
        """
        existing = await self.get_by_user_id(user_id)
        if existing is None:
            return None

        current_preferences = existing.preferences or {}
        merged_preferences = {**current_preferences, **preferences}

        await self.session.execute(
            update(self.model)
            .where(self.model.id == existing.id)
            .values(
                preferences=merged_preferences,
                profile_version=existing.profile_version + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def update_behavioral_patterns(
        self, user_id: str, behavioral_patterns: Dict[str, Any]
    ) -> Optional[UserProfile]:
        """
        Update the behavioral patterns for a user profile.

        Merges the provided patterns with existing patterns (shallow merge),
        increments profile_version, and updates the timestamp.

        Args:
            user_id: The unique string identifier for the user.
            behavioral_patterns: Dictionary of pattern key-value pairs to merge.
                                 Example: {"morning_routine": "exercise",
                                           "work_hours": "9-17"}

        Returns:
            The updated UserProfile instance if found, None if no profile
            exists for the given user_id.
        """
        existing = await self.get_by_user_id(user_id)
        if existing is None:
            return None

        current_patterns = existing.behavioral_patterns or {}
        merged_patterns = {**current_patterns, **behavioral_patterns}

        await self.session.execute(
            update(self.model)
            .where(self.model.id == existing.id)
            .values(
                behavioral_patterns=merged_patterns,
                profile_version=existing.profile_version + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def update_context_summary(
        self, user_id: str, context_summary: str
    ) -> Optional[UserProfile]:
        """
        Update the context summary narrative for a user profile.

        The context summary provides a narrative description of the user's
        current context for AI reference during conversation.

        Args:
            user_id: The unique string identifier for the user.
            context_summary: Narrative text summarizing current user context.

        Returns:
            The updated UserProfile instance if found, None if no profile
            exists for the given user_id.
        """
        existing = await self.get_by_user_id(user_id)
        if existing is None:
            return None

        await self.session.execute(
            update(self.model)
            .where(self.model.id == existing.id)
            .values(
                context_summary=context_summary,
                profile_version=existing.profile_version + 1,
                updated_at=datetime.now(timezone.utc),
            )
        )
        await self.session.flush()
        await self.session.refresh(existing)
        return existing

    async def get_or_create_default(
        self, user_id: str, defaults: Optional[Dict[str, Any]] = None
    ) -> UserProfile:
        """
        Retrieve an existing profile or create one with default values.

        This is the primary entry point for ensuring a user profile exists.
        Used during chat interactions and profile retrieval to guarantee
        a profile is always available for the single-user MVP.

        Args:
            user_id: The unique string identifier for the user.
            defaults: Optional dictionary of default field values for new
                      profile creation. If not provided, uses system defaults:
                      - display_name: "User"
                      - consent_tier: "Suggestive"
                      - traits: {}
                      - preferences: {}
                      - behavioral_patterns: {}

        Returns:
            The existing or newly created UserProfile instance.
        """
        existing = await self.get_by_user_id(user_id)
        if existing is not None:
            return existing

        default_data: Dict[str, Any] = {
            "user_id": user_id,
            "display_name": "User",
            "consent_tier": "Suggestive",
            "traits": {},
            "preferences": {},
            "behavioral_patterns": {},
            "context_summary": None,
            "profile_version": 1,
        }

        if defaults:
            default_data.update(defaults)

        return await self.create(default_data)
