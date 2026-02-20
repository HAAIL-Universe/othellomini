"""
Database module for OthelloMini backend.

Provides async SQLAlchemy engine, session factory, and declarative Base model
for SQLite with aiosqlite driver. All repository layer code imports Base and
get_async_session from this module.

Usage:
    from backend.database import Base, get_async_session, engine

    # In FastAPI dependency injection:
    async def get_db():
        async for session in get_async_session():
            yield session

    # In Alembic migrations:
    from backend.database import Base
    target_metadata = Base.metadata
"""

from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from backend.config import get_settings


class Base(AsyncAttrs, DeclarativeBase):
    """
    Declarative base class for all SQLAlchemy ORM models.

    Combines AsyncAttrs mixin for lazy-loading async attribute access
    with DeclarativeBase for model declaration. All models in
    backend/models/ inherit from this class.
    """

    pass


def _create_engine(database_url: str) -> AsyncEngine:
    """
    Create and configure an async SQLAlchemy engine.

    Args:
        database_url: Database connection string with async driver
                      (e.g., 'sqlite+aiosqlite:///data/othello_mini.db').

    Returns:
        Configured AsyncEngine instance.

    Notes:
        - echo is disabled for production; enable via log level if needed.
        - pool_pre_ping ensures stale connections are detected.
        - For SQLite, connect_args enables WAL mode and foreign key enforcement.
    """
    connect_args = {}

    # SQLite-specific configuration
    if "sqlite" in database_url:
        connect_args["check_same_thread"] = False

    return create_async_engine(
        database_url,
        echo=False,
        future=True,
        connect_args=connect_args,
    )


def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """
    Enable SQLite foreign key enforcement on each new connection.

    SQLite does not enforce foreign keys by default; this pragma must
    be set per-connection. Also enables WAL journal mode for better
    concurrent read performance.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


settings = get_settings()
engine = _create_engine(settings.database_url_async)

# Register SQLite-specific event listeners
if "sqlite" in settings.database_url_async:
    event.listen(engine.sync_engine, "connect", _enable_sqlite_foreign_keys)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async database session for dependency injection.

    This is the primary entry point for FastAPI route handlers to
    obtain a database session. The session is automatically closed
    after the request completes, and any uncommitted changes are
    rolled back on exception.

    Yields:
        AsyncSession: A SQLAlchemy async session bound to the engine.

    Example:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_session)):
            result = await db.execute(select(Item))
            return result.scalars().all()
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


async def init_db() -> None:
    """
    Initialize the database by creating all tables defined in Base.metadata.

    This is a convenience function for development and testing. In production,
    Alembic migrations should be used instead to manage schema changes.

    This function creates tables that don't exist yet without dropping
    existing tables or data.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    """
    Dispose of the database engine and close all connections.

    Should be called during application shutdown to cleanly release
    database resources.
    """
    await engine.dispose()
