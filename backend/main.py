"""
FastAPI application entry point for OthelloMini.

Registers all API routers, configures CORS middleware, global error handling,
request logging, and manages application startup/shutdown lifecycle events
including database initialization and default user profile seeding.
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.database import engine, async_session_factory, Base
from backend.api.chat import router as chat_router
from backend.api.profile import router as profile_router
from backend.api.suggestions import router as suggestions_router
from backend.api.conversations import router as conversations_router
from backend.api.health import router as health_router
from backend.middleware.error_handler import register_exception_handlers
from backend.middleware.logging import LoggingMiddleware
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def _seed_default_user() -> None:
    """Seed the default user profile if it does not exist."""
    from backend.repositories.profile_repository import ProfileRepository

    async with async_session_factory() as session:
        repo = ProfileRepository(session)
        existing = await repo.get_by_user_id(settings.DEFAULT_USER_ID)
        if existing is None:
            logger.info(
                "Seeding default user profile",
                extra={"user_id": settings.DEFAULT_USER_ID},
            )
            await repo.create(
                user_id=settings.DEFAULT_USER_ID,
                display_name="User",
                consent_tier="Suggestive",
                traits={
                    "openness": 0.7,
                    "conscientiousness": 0.6,
                    "extraversion": 0.5,
                    "agreeableness": 0.65,
                    "neuroticism": 0.45,
                    "risk_tolerance": "medium",
                    "decision_style": "analytical",
                },
                preferences={
                    "communication_style": "conversational",
                    "focus_areas": ["productivity", "wellness"],
                    "notification_frequency": "daily",
                },
                context_summary="New user exploring AI life companion features.",
            )
            await session.commit()
            logger.info("Default user profile seeded successfully")
        else:
            logger.info(
                "Default user profile already exists",
                extra={"user_id": settings.DEFAULT_USER_ID},
            )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    On startup: creates database tables (if not exist) and seeds default user.
    On shutdown: disposes database engine connections.
    """
    logger.info("OthelloMini API starting up...")

    # Create all tables if they don't exist (fallback for non-Alembic environments)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables verified/created")

    # Seed default user profile
    await _seed_default_user()

    logger.info(
        "OthelloMini API ready",
        extra={
            "version": "1.0.0",
            "openai_model": settings.OPENAI_MODEL,
            "default_user_id": settings.DEFAULT_USER_ID,
        },
    )

    yield

    # Shutdown
    logger.info("OthelloMini API shutting down...")
    await engine.dispose()
    logger.info("Database connections closed")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    Returns:
        Configured FastAPI application with all routers, middleware, and
        exception handlers registered.
    """
    app = FastAPI(
        title="OthelloMini API",
        description=(
            "Ethics-first AI chat companion with consent-gated personalized assistance. "
            "All AI-generated suggestions pass through the Othello ethical gatekeeper "
            "before presentation to the user."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # --- CORS Middleware ---
    cors_origins = [
        origin.strip()
        for origin in settings.CORS_ORIGINS.split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- Request Logging Middleware ---
    app.add_middleware(LoggingMiddleware)

    # --- Global Exception Handlers ---
    register_exception_handlers(app)

    # --- API Routers ---
    app.include_router(
        health_router,
        prefix="/api/v1",
        tags=["health"],
    )
    app.include_router(
        chat_router,
        prefix="/api/v1",
        tags=["chat"],
    )
    app.include_router(
        profile_router,
        prefix="/api/v1",
        tags=["profile"],
    )
    app.include_router(
        suggestions_router,
        prefix="/api/v1",
        tags=["suggestions"],
    )
    app.include_router(
        conversations_router,
        prefix="/api/v1",
        tags=["conversations"],
    )

    # --- Root Redirect ---
    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        """Root endpoint redirecting to API documentation."""
        return {
            "name": "OthelloMini API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


# Application instance used by uvicorn
app = create_app()
