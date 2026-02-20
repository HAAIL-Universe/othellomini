"""
SQLAlchemy models for OthelloMini database tables.

Exports all ORM models for centralized import throughout the application.
These models map directly to the database schema defined in the schema contract:
- UserProfile: persistent user psychological model and consent settings
- Conversation: chat message history for user interactions
- Suggestion: AI-generated action suggestions with ethical gating metadata
"""

from backend.models.user_profile import UserProfile
from backend.models.conversation import Conversation
from backend.models.suggestion import Suggestion

__all__ = [
    "UserProfile",
    "Conversation",
    "Suggestion",
]
