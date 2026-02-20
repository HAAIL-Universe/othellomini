"""
FastAPI dependency injection providers for database sessions and service instances.

This module defines async generator dependencies that provide properly scoped
database sessions and fully-wired service instances to API route handlers.
Dependencies follow the unidirectional flow: API → Service → Repository → Database.

All dependencies are designed to be used with FastAPI's Depends() mechanism,
ensuring proper lifecycle management (session creation, commit/rollback, cleanup).

Layer boundary: This module may import from database, repositories, and services.
It MUST NOT import from other API modules, raw SQL, or external AI clients directly.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import async_session_factory
from backend.repositories.profile_repository import ProfileRepository
from backend.repositories.conversation_repository import ConversationRepository
from backend.repositories.suggestion_repository import SuggestionRepository
from backend.services.ai_service import AIService
from backend.services.othello_service import OthelloService
from backend.services.profile_service import ProfileService
from backend.services.chat_service import ChatService
from backend.config import settings


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async database session with automatic commit/rollback lifecycle.

    Creates a new SQLAlchemy AsyncSession from the session factory, yields it
    for use in the request handler, commits on success, rolls back on exception,
    and always closes the session on completion.

    Yields:
        AsyncSession: A SQLAlchemy async database session scoped to the request.

    Raises:
        Exception: Re-raises any exception after performing rollback.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_profile_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[ProfileRepository, None]:
    """
    Provide a ProfileRepository instance with a scoped database session.

    This dependency creates its own session lifecycle when used standalone.
    For shared-session usage within a single request, use get_db_session()
    and construct repositories manually.

    Yields:
        ProfileRepository: Repository instance for user_profiles table operations.
    """
    async for session in get_db_session():
        yield ProfileRepository(session)


async def get_conversation_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[ConversationRepository, None]:
    """
    Provide a ConversationRepository instance with a scoped database session.

    Yields:
        ConversationRepository: Repository instance for conversations table operations.
    """
    async for session in get_db_session():
        yield ConversationRepository(session)


async def get_suggestion_repository(
    session: AsyncSession = None,
) -> AsyncGenerator[SuggestionRepository, None]:
    """
    Provide a SuggestionRepository instance with a scoped database session.

    Yields:
        SuggestionRepository: Repository instance for suggestions table operations.
    """
    async for session in get_db_session():
        yield SuggestionRepository(session)


def get_ai_service() -> AIService:
    """
    Provide an AIService instance configured with application settings.

    Creates a new AIService with the OpenAI API key and model configuration
    from the application settings. This is a synchronous factory since
    AIService initialization does not require async operations.

    Returns:
        AIService: Service instance for OpenAI GPT-4 API integration.
    """
    return AIService(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
    )


def get_othello_service() -> OthelloService:
    """
    Provide an OthelloService instance for ethical gating.

    Creates a new OthelloService instance that implements the rule-based
    ethical filter with consent tier assignment and reasoning generation.
    This is the core ethical gatekeeper — all suggestions MUST pass through
    this service before reaching the user.

    Returns:
        OthelloService: Service instance for consent-tier ethical gating.
    """
    return OthelloService()


async def get_profile_service() -> AsyncGenerator[ProfileService, None]:
    """
    Provide a ProfileService instance with all required dependencies.

    Creates a ProfileRepository with a scoped database session and wires
    it into a ProfileService instance. The session lifecycle is managed
    by the inner get_db_session dependency.

    Yields:
        ProfileService: Service instance for user profile management.
    """
    async with async_session_factory() as session:
        try:
            profile_repo = ProfileRepository(session)
            yield ProfileService(
                profile_repository=profile_repo,
                default_user_id=settings.default_user_id,
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_chat_service() -> AsyncGenerator[ChatService, None]:
    """
    Provide a fully-wired ChatService instance with all dependencies.

    Creates all required repositories with a shared database session and
    wires them together with AIService and OthelloService into a ChatService.
    The shared session ensures transactional consistency across all operations
    within a single chat request.

    This is the primary dependency for the /chat endpoint. The ChatService
    orchestrates AI response generation, ethical gating, conversation
    persistence, and profile updates — all within a single session scope.

    Yields:
        ChatService: Fully configured service for chat interaction orchestration.
    """
    async with async_session_factory() as session:
        try:
            # Create repositories sharing the same session for transactional consistency
            profile_repo = ProfileRepository(session)
            conversation_repo = ConversationRepository(session)
            suggestion_repo = SuggestionRepository(session)

            # Create service dependencies
            ai_service = get_ai_service()
            othello_service = get_othello_service()

            # Wire everything into ChatService
            chat_service = ChatService(
                ai_service=ai_service,
                othello_service=othello_service,
                profile_repo=profile_repo,
                conversation_repo=conversation_repo,
                suggestion_repo=suggestion_repo,
            )

            yield chat_service
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_suggestion_repo_with_session() -> AsyncGenerator[SuggestionRepository, None]:
    """
    Provide a SuggestionRepository with a managed session for standalone use.

    Used by suggestion endpoints (approve, deny, list) that need direct
    repository access without the full ChatService orchestration.

    Yields:
        SuggestionRepository: Repository instance with managed session lifecycle.
    """
    async with async_session_factory() as session:
        try:
            yield SuggestionRepository(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_conversation_repo_with_session() -> AsyncGenerator[ConversationRepository, None]:
    """
    Provide a ConversationRepository with a managed session for standalone use.

    Used by conversation history endpoints that need direct repository access
    without the full ChatService orchestration.

    Yields:
        ConversationRepository: Repository instance with managed session lifecycle.
    """
    async with async_session_factory() as session:
        try:
            yield ConversationRepository(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_profile_repo_with_session() -> AsyncGenerator[ProfileRepository, None]:
    """
    Provide a ProfileRepository with a managed session for standalone use.

    Used by profile endpoints that need direct repository access alongside
    ProfileService operations.

    Yields:
        ProfileRepository: Repository instance with managed session lifecycle.
    """
    async with async_session_factory() as session:
        try:
            yield ProfileRepository(session)
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
