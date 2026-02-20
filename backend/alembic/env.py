"""Alembic environment script for migration execution."""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool, create_engine

# Ensure backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.database import Base
from backend.models import UserProfile, Conversation, Suggestion  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """Resolve database URL from environment or alembic config."""
    url = os.environ.get("DATABASE_URL", None)
    if url:
        # Convert async URL to sync for Alembic
        return url.replace("+aiosqlite", "")
    url = config.get_main_option("sqlalchemy.url", "sqlite:///data/othello_mini.db")
    return url.replace("+aiosqlite", "")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = _get_url()
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
