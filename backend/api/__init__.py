"""
API package for OthelloMini.

Aggregates all endpoint routers into a single APIRouter for inclusion
in the FastAPI application. All routes are prefixed under /api/v1.
"""

from fastapi import APIRouter

from backend.api.chat import router as chat_router
from backend.api.profile import router as profile_router
from backend.api.suggestions import router as suggestions_router
from backend.api.conversations import router as conversations_router
from backend.api.health import router as health_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router, tags=["health"])
api_router.include_router(chat_router, tags=["chat"])
api_router.include_router(profile_router, tags=["profile"])
api_router.include_router(suggestions_router, tags=["suggestions"])
api_router.include_router(conversations_router, tags=["conversations"])

__all__ = ["api_router"]
