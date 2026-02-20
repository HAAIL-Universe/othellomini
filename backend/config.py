"""
Configuration module for OthelloMini backend.

Loads environment variables via Pydantic Settings with sensible defaults
for local development. All configuration is centralized here to avoid
scattered os.getenv() calls throughout the codebase.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Environment variables can be set directly or via a .env file
    in the backend directory. Pydantic Settings handles type coercion
    and validation automatically.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///data/othello_mini.db"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    openai_timeout: int = 30

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Application
    log_level: str = "INFO"
    default_user_id: str = "default_user"
    max_conversation_history: int = 20

    # API
    api_v1_prefix: str = "/api/v1"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url_async(self) -> str:
        """
        Ensure database URL uses the async SQLite driver.

        Converts 'sqlite:///' to 'sqlite+aiosqlite:///' if needed.
        """
        url = self.database_url
        if url.startswith("sqlite:///") and "aiosqlite" not in url:
            url = url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
        return url


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    Uses lru_cache to ensure settings are loaded once and reused
    across the application lifecycle. Call get_settings.cache_clear()
    to force reload (useful in tests).
    """
    return Settings()
