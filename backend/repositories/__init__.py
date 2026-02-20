"""
Repository layer package for OthelloMini.

Provides data access abstractions for all database tables.
Repositories encapsulate all ORM/SQL logic — services interact
via repository interfaces only.
"""

from backend.repositories.base import BaseRepository
from backend.repositories.profile_repository import ProfileRepository
from backend.repositories.conversation_repository import ConversationRepository
from backend.repositories.suggestion_repository import SuggestionRepository

__all__ = [
    "BaseRepository",
    "ProfileRepository",
    "ConversationRepository",
    "SuggestionRepository",
]
