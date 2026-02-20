"""Database initialization script: create tables and seed default user profile."""

import asyncio
import sys

from backend.database import engine, Base, async_session_factory
from backend.repositories.profile_repository import ProfileRepository
from backend.utils.logger import get_logger

# Import all models so Base.metadata is fully populated
import backend.models  # noqa: F401

logger = get_logger(__name__)

DEFAULT_USER_ID = "default-user"
DEFAULT_CONSENT_TIER = "Passive"


async def init_database() -> None:
    """Create all tables and seed the default user profile."""
    logger.info("Starting database initialization")

    # Create all tables from SQLAlchemy metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

    # Seed default user profile
    async with async_session_factory() as session:
        try:
            repo = ProfileRepository(session)
            existing = await repo.get_by_user_id(DEFAULT_USER_ID)

            if existing is not None:
                logger.info(
                    "Default user profile already exists",
                    extra={"user_id": DEFAULT_USER_ID},
                )
            else:
                await repo.upsert(
                    user_id=DEFAULT_USER_ID,
                    data={
                        "display_name": "Default User",
                        "consent_tier": DEFAULT_CONSENT_TIER,
                        "traits": {},
                        "preferences": {},
                        "behavioral_patterns": {},
                        "context_summary": None,
                        "profile_version": 1,
                    },
                )
                await session.commit()
                logger.info(
                    "Default user profile created",
                    extra={
                        "user_id": DEFAULT_USER_ID,
                        "consent_tier": DEFAULT_CONSENT_TIER,
                    },
                )
        except Exception:
            await session.rollback()
            logger.exception("Failed to seed default user profile")
            raise

    logger.info("Database initialization complete")


async def main() -> None:
    """Entry point for the init_db script."""
    try:
        await init_database()
    except Exception:
        logger.exception("Database initialization failed")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
