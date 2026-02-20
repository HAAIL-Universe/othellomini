"""
Pydantic schemas for OthelloMini API request/response validation.

Exports all schema classes for centralized import throughout the application.
"""

from backend.schemas.chat import (
    ChatContext,
    ChatMetadata,
    ChatRequest,
    ChatResponse,
)
from backend.schemas.conversation import (
    ConversationDetail,
    ConversationListResponse,
)
from backend.schemas.profile import (
    ContextSummary,
    ProfileClearResponse,
    ProfileTraits,
    ProfileUpdateRequest,
    UserPreferences,
    UserProfileResponse,
)
from backend.schemas.suggestion import (
    EthicalReasoning,
    SuggestionApproveRequest,
    SuggestionApproveResponse,
    SuggestionDenyRequest,
    SuggestionDenyResponse,
    SuggestionListResponse,
    SuggestionResponse,
)

__all__ = [
    # Chat schemas
    "ChatContext",
    "ChatMetadata",
    "ChatRequest",
    "ChatResponse",
    # Conversation schemas
    "ConversationDetail",
    "ConversationListResponse",
    # Profile schemas
    "ContextSummary",
    "ProfileClearResponse",
    "ProfileTraits",
    "ProfileUpdateRequest",
    "UserPreferences",
    "UserProfileResponse",
    # Suggestion schemas
    "EthicalReasoning",
    "SuggestionApproveRequest",
    "SuggestionApproveResponse",
    "SuggestionDenyRequest",
    "SuggestionDenyResponse",
    "SuggestionListResponse",
    "SuggestionResponse",
]
