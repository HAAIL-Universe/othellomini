"""
ProfileService for user profile management, trait updates, and consent tier changes.

Provides business logic for managing the persistent user profile including
retrieving profile summaries, updating consent tier settings, modifying
psychological traits, preferences, and behavioral patterns. This service
acts as the intermediary between the API layer and the ProfileRepository,
enforcing business rules and data validation before persistence.

This service layer is responsible for:
- Ensuring profile existence (get-or-create pattern for single-user MVP)
- Validating consent tier transitions
- Coordinating profile field updates with version tracking
- Formatting profile data for API responses

Layer boundary: Services may import from repositories and schemas only.
Services MUST NOT import from api layer, FastAPI Request/Response objects,
or raw SQL.
"""

import logging
from typing import Any, Dict, List, Optional

from backend.repositories.profile_repository import ProfileRepository
from backend.models.user_profile import UserProfile


logger = logging.getLogger(__name__)

# Default user ID for single-user MVP
DEFAULT_USER_ID = "default_user"

# Valid consent tiers in order of increasing autonomy
CONSENT_TIERS = ["Passive", "Suggestive", "Active", "Autonomous"]

# Consent tier descriptions for user-facing display
CONSENT_TIER_DESCRIPTIONS: Dict[str, str] = {
    "Passive": "AI observes and learns but does not make suggestions. Information is gathered silently.",
    "Suggestive": "AI may offer gentle suggestions when relevant, but takes no action without explicit approval.",
    "Active": "AI proactively suggests actions and may prepare drafts or plans for your review before execution.",
    "Autonomous": "AI may take pre-approved categories of actions on your behalf, reporting results afterward.",
}


class ProfileService:
    """
    Service for user profile management and consent tier operations.

    Encapsulates business logic for profile CRUD operations, consent tier
    validation, and profile data formatting. Delegates all persistence
    operations to the ProfileRepository.

    Attributes:
        profile_repository: Repository instance for user_profiles table access.
        default_user_id: The fixed user_id for the single-user MVP scope.
    """

    def __init__(
        self,
        profile_repository: ProfileRepository,
        default_user_id: str = DEFAULT_USER_ID,
    ) -> None:
        """
        Initialize the ProfileService with a profile repository.

        Args:
            profile_repository: ProfileRepository instance for data access.
            default_user_id: The fixed user_id for single-user MVP. Defaults
                             to 'default_user'.
        """
        self.profile_repository = profile_repository
        self.default_user_id = default_user_id

    async def get_profile(self, user_id: Optional[str] = None) -> UserProfile:
        """
        Retrieve the user profile, creating a default one if it doesn't exist.

        This is the primary entry point for profile retrieval. For the
        single-user MVP, it uses the default_user_id if no user_id is provided.
        Guarantees a profile always exists via the get-or-create pattern.

        Args:
            user_id: Optional user identifier. Defaults to the configured
                     default_user_id if not provided.

        Returns:
            The UserProfile instance for the requested user.
        """
        resolved_user_id = user_id or self.default_user_id
        logger.info("Retrieving profile for user_id=%s", resolved_user_id)

        profile = await self.profile_repository.get_or_create_default(
            user_id=resolved_user_id
        )

        logger.info(
            "Profile retrieved: user_id=%s, version=%d, consent_tier=%s",
            profile.user_id,
            profile.profile_version,
            profile.consent_tier,
        )
        return profile

    async def get_profile_summary(
        self, user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a formatted summary of the user profile for API responses.

        Returns a dictionary with the profile data structured for the
        frontend display, including top traits, current consent tier,
        and profile metadata.

        Args:
            user_id: Optional user identifier. Defaults to the configured
                     default_user_id if not provided.

        Returns:
            Dictionary containing:
                - user_id: The user's identifier
                - display_name: The user's display name
                - consent_tier: Current consent tier string
                - consent_tier_description: Human-readable tier description
                - traits: Full traits dictionary
                - top_traits: List of top 3 traits by value (descending)
                - preferences: Full preferences dictionary
                - behavioral_patterns: Full behavioral patterns dictionary
                - context_summary: Current context narrative or None
                - profile_version: Current version number
                - created_at: Profile creation timestamp (ISO format)
                - updated_at: Last update timestamp (ISO format)
        """
        profile = await self.get_profile(user_id)
        return self._format_profile_summary(profile)

    async def update_consent_tier(
        self, consent_tier: str, user_id: Optional[str] = None
    ) -> UserProfile:
        """
        Update the user's consent tier setting.

        Validates the consent tier value before persisting the change.
        This is a critical operation as it controls the ethical gating
        behavior for all future AI suggestions.

        Args:
            consent_tier: The new consent tier value. Must be one of:
                          'Passive', 'Suggestive', 'Active', 'Autonomous'.
            user_id: Optional user identifier. Defaults to the configured
                     default_user_id if not provided.

        Returns:
            The updated UserProfile instance.

        Raises:
            ValueError: If consent_tier is not a valid tier value.
            RuntimeError: If the profile could not be found or updated.
        """
        resolved_user_id = user_id or self.default_user_id

        # Validate consent tier
        if consent_tier not in CONSENT_TIERS:
            raise ValueError(
                f"Invalid consent tier '{consent_tier}'. "
                f"Must be one of: {', '.join(CONSENT_TIERS)}"
            )

        # Ensure profile exists before updating
        await self.get_profile(resolved_user_id)

        logger.info(
            "Updating consent tier for user_id=%s to '%s'",
            resolved_user_id,
            consent_tier,
        )

        updated_profile = await self.profile_repository.update_consent_tier(
            user_id=resolved_user_id,
            consent_tier=consent_tier,
        )

        if updated_profile is None:
            raise RuntimeError(
                f"Failed to update consent tier for user_id '{resolved_user_id}'. "
                "Profile not found after existence check."
            )

        logger.info(
            "Consent tier updated: user_id=%s, tier=%s, version=%d",
            updated_profile.user_id,
            updated_profile.consent_tier,
            updated_profile.profile_version,
        )

        return updated_profile

    async def update_profile(
        self,
        updates: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> UserProfile:
        """
        Update multiple profile fields at once.

        Supports updating display_name, consent_tier, traits, preferences,
        behavioral_patterns, and context_summary. Validates consent_tier
        if included in updates. For traits, preferences, and behavioral_patterns,
        performs a merge (shallow) with existing values rather than replacement.

        Args:
            updates: Dictionary of field names and their new values.
                     Supported keys: display_name, consent_tier, traits,
                     preferences, behavioral_patterns, context_summary.
            user_id: Optional user identifier. Defaults to the configured
                     default_user_id if not provided.

        Returns:
            The updated UserProfile instance.

        Raises:
            ValueError: If consent_tier is included but invalid, or if
                        unsupported fields are provided.
        """
        resolved_user_id = user_id or self.default_user_id

        # Validate consent tier if present
        if "consent_tier" in updates:
            if updates["consent_tier"] not in CONSENT_TIERS:
                raise ValueError(
                    f"Invalid consent tier '{updates['consent_tier']}'. "
                    f"Must be one of: {', '.join(CONSENT_TIERS)}"
                )

        # Validate that only supported fields are being updated
        supported_fields = {
            "display_name",
            "consent_tier",
            "traits",
            "preferences",
            "behavioral_patterns",
            "context_summary",
        }
        unsupported = set(updates.keys()) - supported_fields
        if unsupported:
            raise ValueError(
                f"Unsupported profile fields: {', '.join(sorted(unsupported))}. "
                f"Supported fields: {', '.join(sorted(supported_fields))}"
            )

        logger.info(
            "Updating profile for user_id=%s, fields=%s",
            resolved_user_id,
            list(updates.keys()),
        )

        # Handle merge-based fields separately
        profile = await self.get_profile(resolved_user_id)

        if "traits" in updates and isinstance(updates["traits"], dict):
            await self.profile_repository.update_traits(
                user_id=resolved_user_id,
                traits=updates["traits"],
            )

        if "preferences" in updates and isinstance(updates["preferences"], dict):
            await self.profile_repository.update_preferences(
                user_id=resolved_user_id,
                preferences=updates["preferences"],
            )

        if "behavioral_patterns" in updates and isinstance(
            updates["behavioral_patterns"], dict
        ):
            await self.profile_repository.update_behavioral_patterns(
                user_id=resolved_user_id,
                behavioral_patterns=updates["behavioral_patterns"],
            )

        if "context_summary" in updates:
            await self.profile_repository.update_context_summary(
                user_id=resolved_user_id,
                context_summary=updates["context_summary"],
            )

        # Handle direct field updates (display_name, consent_tier)
        direct_updates: Dict[str, Any] = {}
        if "display_name" in updates:
            direct_updates["display_name"] = updates["display_name"]
        if "consent_tier" in updates:
            direct_updates["consent_tier"] = updates["consent_tier"]

        if direct_updates:
            await self.profile_repository.upsert(
                user_id=resolved_user_id,
                data=direct_updates,
            )

        # Re-fetch the fully updated profile
        updated_profile = await self.get_profile(resolved_user_id)

        logger.info(
            "Profile updated: user_id=%s, version=%d",
            updated_profile.user_id,
            updated_profile.profile_version,
        )

        return updated_profile

    async def update_traits(
        self,
        traits: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> UserProfile:
        """
        Update psychological traits for the user profile.

        Performs a shallow merge with existing traits — new values override
        existing ones for the same keys, existing keys not in the update
        are preserved.

        Args:
            traits: Dictionary of trait key-value pairs to merge.
                    Example: {"openness": 0.8, "conscientiousness": 0.7}
            user_id: Optional user identifier. Defaults to the configured
                     default_user_id if not provided.

        Returns:
            The updated UserProfile instance.

        Raises:
            RuntimeError: If the profile could not be found or updated.
        """
        resolved_user_id = user_id or self.default_user_id

        # Ensure profile exists
        await self.get_profile(resolved_user_id)

        logger.info(
            "Updating traits for user_id=%s, keys=%s",
            resolved_user_id,
            list(traits.keys()),
        )

        updated_profile = await self.profile_repository.update_traits(
            user_id=resolved_user_id,
            traits=traits,
        )

        if updated_profile is None:
            raise RuntimeError(
                f"Failed to update traits for user_id '{resolved_user_id}'. "
                "Profile not found after existence check."
            )

        logger.info(
            "Traits updated: user_id=%s, version=%d",
            updated_profile.user_id,
            updated_profile.profile_version,
        )

        return updated_profile

    async def update_preferences(
        self,
        preferences: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> UserProfile:
        """
        Update user preferences for the user profile.

        Performs a shallow merge with existing preferences — new values
        override existing ones for the same keys.

        Args:
            preferences: Dictionary of preference key-value pairs to merge.
                         Example: {"communication_style": "direct",
                                   "priority_areas": ["health", "productivity"]}
            user_id: Optional user identifier. Defaults to the configured
                     default_user_id if not provided.

        Returns:
            The updated UserProfile instance.

        Raises:
            RuntimeError: If the profile could not be found or updated.
        """
        resolved_user_id = user_id or self.default_user_id

        # Ensure profile exists
        await self.get_profile(resolved_user_id)

        logger.info(
            "Updating preferences for user_id=%s, keys=%s",
            resolved_user_id,
            list(preferences.keys()),
        )

        updated_profile = await self.profile_repository.update_preferences(
            user_id=resolved_user_id,
            preferences=preferences,
        )

        if updated_profile is None:
            raise RuntimeError(
                f"Failed to update preferences for user_id '{resolved_user_id}'. "
                "Profile not found after existence check."
            )

        logger.info(
            "Preferences updated: user_id=%s, version=%d",
            updated_profile.user_id,
            updated_profile.profile_version,
        )

        return updated_profile

    async def update_behavioral_patterns(
        self,
        behavioral_patterns: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> UserProfile:
        """
        Update behavioral patterns for the user profile.

        Performs a shallow merge with existing behavioral patterns — new values
        override existing ones for the same keys.

        Args:
            behavioral_patterns: Dictionary of pattern key-value pairs to merge.
                                 Example: {"morning_routine": "exercise",
                                           "work_hours": "9-17"}
            user_id: Optional user identifier. Defaults to the configured
                     default_user_id if not provided.

        Returns:
            The updated UserProfile instance.

        Raises:
            RuntimeError: If the profile could not be found or updated.
        """
        resolved_user_id = user_id or self.default_user_id

        # Ensure profile exists
        await self.get_profile(resolved_user_id)

        logger.info(
            "Updating behavioral patterns for user_id=%s, keys=%s",
            resolved_user_id,
            list(behavioral_patterns.keys()),
        )

        updated_profile = await self.profile_repository.update_behavioral_patterns(
            user_id=resolved_user_id,
            behavioral_patterns=behavioral_patterns,
        )

        if updated_profile is None:
            raise RuntimeError(
                f"Failed to update behavioral patterns for user_id '{resolved_user_id}'. "
                "Profile not found after existence check."
            )

        logger.info(
            "Behavioral patterns updated: user_id=%s, version=%d",
            updated_profile.user_id,
            updated_profile.profile_version,
        )

        return updated_profile

    async def update_context_summary(
        self,
        context_summary: str,
        user_id: Optional[str] = None,
    ) -> UserProfile:
        """
        Update the context summary narrative for the user profile.

        The context summary is a narrative description of the user's current
        context, used by the AI service for generating contextually relevant
        responses and suggestions.

        Args:
            context_summary: Narrative text summarizing current user context.
            user_id: Optional user identifier. Defaults to the configured
                     default_user_id if not provided.

        Returns:
            The updated UserProfile instance.

        Raises:
            RuntimeError: If the profile could not be found or updated.
        """
        resolved_user_id = user_id or self.default_user_id

        # Ensure profile exists
        await self.get_profile(resolved_user_id)

        logger.info(
            "Updating context summary for user_id=%s",
            resolved_user_id,
        )

        updated_profile = await self.profile_repository.update_context_summary(
            user_id=resolved_user_id,
            context_summary=context_summary,
        )

        if updated_profile is None:
            raise RuntimeError(
                f"Failed to update context summary for user_id '{resolved_user_id}'. "
                "Profile not found after existence check."
            )

        logger.info(
            "Context summary updated: user_id=%s, version=%d",
            updated_profile.user_id,
            updated_profile.profile_version,
        )

        return updated_profile

    def _format_profile_summary(self, profile: UserProfile) -> Dict[str, Any]:
        """
        Format a UserProfile instance into a summary dictionary for API responses.

        Args:
            profile: The UserProfile instance to format.

        Returns:
            Dictionary containing formatted profile data with top traits.
        """
        # Extract top 3 traits by value
        top_traits = []
        if profile.traits:
            sorted_traits = sorted(
                profile.traits.items(),
                key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0,
                reverse=True,
            )
            top_traits = [
                {"name": name, "value": value}
                for name, value in sorted_traits[:3]
            ]

        return {
            "user_id": profile.user_id,
            "display_name": profile.display_name,
            "consent_tier": profile.consent_tier,
            "consent_tier_description": CONSENT_TIER_DESCRIPTIONS.get(
                profile.consent_tier, ""
            ),
            "traits": profile.traits or {},
            "top_traits": top_traits,
            "preferences": profile.preferences or {},
            "behavioral_patterns": profile.behavioral_patterns or {},
            "context_summary": profile.context_summary,
            "profile_version": profile.profile_version,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }
