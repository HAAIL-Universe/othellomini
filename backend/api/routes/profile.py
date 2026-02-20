"""Profile management endpoints."""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from backend.schemas.profile import (
    ProfileResponse,
    ProfileUpdateRequest,
    PreferencesSchema,
    TraitsSchema,
    ContextSummarySchema,
    ConsentTier,
)
from backend.services.profile_service import ProfileService
from backend.api.dependencies import get_profile_service, get_user_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/profile", tags=["profile"])

# Re-export for interface map compatibility
ProfileSummaryResponse = ProfileResponse


def _map_consent_tier(db_tier: str) -> ConsentTier:
    """Map database consent tier string to schema enum."""
    mapping = {
        "Passive": ConsentTier.PASSIVE,
        "Suggestive": ConsentTier.SUGGESTIVE,
        "Active": ConsentTier.ACTIVE,
        "Autonomous": ConsentTier.AUTONOMOUS,
    }
    return mapping.get(db_tier, ConsentTier.PASSIVE)


def _consent_tier_to_db(tier: ConsentTier) -> str:
    """Map schema consent tier enum to database string."""
    mapping = {
        ConsentTier.PASSIVE: "Passive",
        ConsentTier.SUGGESTIVE: "Suggestive",
        ConsentTier.ACTIVE: "Active",
        ConsentTier.AUTONOMOUS: "Autonomous",
    }
    return mapping[tier]


def _build_traits(raw: Any) -> TraitsSchema:
    """Build TraitsSchema from raw DB JSON."""
    if isinstance(raw, dict):
        return TraitsSchema(**{k: v for k, v in raw.items() if k in TraitsSchema.model_fields})
    return TraitsSchema()


def _build_preferences(raw: Any) -> PreferencesSchema:
    """Build PreferencesSchema from raw DB JSON."""
    if isinstance(raw, dict):
        return PreferencesSchema(**{k: v for k, v in raw.items() if k in PreferencesSchema.model_fields})
    return PreferencesSchema()


def _build_context_summary(raw: Any) -> Optional[ContextSummarySchema]:
    """Build ContextSummarySchema from raw DB text/JSON."""
    if raw is None:
        return None
    if isinstance(raw, dict):
        return ContextSummarySchema(**{k: v for k, v in raw.items() if k in ContextSummarySchema.model_fields})
    return None


def _profile_to_response(profile: Any) -> ProfileResponse:
    """Convert a UserProfile ORM instance to ProfileResponse."""
    return ProfileResponse(
        user_id=profile.user_id,
        consent_tier=_map_consent_tier(profile.consent_tier),
        traits=_build_traits(profile.traits),
        preferences=_build_preferences(profile.preferences),
        context_summary=_build_context_summary(getattr(profile, "context_summary", None)),
        profile_version=profile.profile_version,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get("", response_model=ProfileResponse)
async def get_profile(
    user_id: str = Depends(get_user_id),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Retrieve user profile including consent tier and profile data."""
    try:
        profile = await profile_service.get_profile(user_id)
        return _profile_to_response(profile)
    except Exception as exc:
        logger.error("Failed to retrieve profile for user_id=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user profile.",
        ) from exc


@router.patch("", response_model=ProfileResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    user_id: str = Depends(get_user_id),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Update consent tier and/or preferences."""
    if request.consent_tier is None and request.preferences is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one of 'consent_tier' or 'preferences' must be provided.",
        )

    try:
        updates: Dict[str, Any] = {}

        if request.consent_tier is not None:
            updates["consent_tier"] = _consent_tier_to_db(request.consent_tier)

        if request.preferences is not None:
            updates["preferences"] = request.preferences.model_dump(exclude_none=True)

        profile = await profile_service.update_profile(updates, user_id)
        return _profile_to_response(profile)

    except ValueError as exc:
        logger.warning("Invalid profile update for user_id=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.error("Failed to update profile for user_id=%s: %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile.",
        ) from exc
