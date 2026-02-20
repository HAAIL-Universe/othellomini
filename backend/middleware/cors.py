"""CORS configuration middleware for frontend cross-origin requests."""

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

CORS_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

_DEFAULT_HEADERS: List[str] = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
    "X-Requested-With",
    "X-Correlation-ID",
]

_DEFAULT_METHODS: List[str] = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]


def setup_cors(app: FastAPI) -> None:
    """Register CORS middleware on the FastAPI application."""
    origins = _resolve_origins(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=_DEFAULT_METHODS,
        allow_headers=_DEFAULT_HEADERS,
        expose_headers=["X-Correlation-ID"],
        max_age=600,
    )


def _resolve_origins(app: FastAPI) -> List[str]:
    """Merge default origins with any configured in app settings."""
    origins = list(CORS_ORIGINS)

    try:
        from config import get_settings
        settings = get_settings()
        if hasattr(settings, "cors_origins_list"):
            for origin in settings.cors_origins_list:
                if origin and origin not in origins:
                    origins.append(origin)
    except Exception:
        pass

    return origins
