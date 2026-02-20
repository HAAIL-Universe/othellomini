"""Global exception handler middleware for structured error responses."""

import traceback
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from utils.logger import get_logger

logger = get_logger(__name__)


class ErrorResponse(BaseModel):
    """Structured error payload."""

    error: str
    detail: str | None = None
    status_code: int = 500
    correlation_id: str | None = None


class AppException(Exception):
    """Application-level exception with HTTP status code."""

    def __init__(self, status_code: int = 400, detail: str = "Bad request", error: str = "app_error") -> None:
        self.status_code = status_code
        self.detail = detail
        self.error = error
        super().__init__(detail)


def _build_error_response(status_code: int, error: str, detail: str | None = None, correlation_id: str | None = None) -> JSONResponse:
    body = ErrorResponse(
        error=error,
        detail=detail,
        status_code=status_code,
        correlation_id=correlation_id,
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


async def error_handler_middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Catch unhandled exceptions and return structured JSON errors."""
    correlation_id = getattr(request.state, "correlation_id", None)
    try:
        return await call_next(request)
    except AppException as exc:
        logger.warning(
            "AppException: %s",
            exc.detail,
            extra={"status_code": exc.status_code, "correlation_id": correlation_id},
        )
        return _build_error_response(exc.status_code, exc.error, exc.detail, correlation_id)
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "Unhandled exception: %s",
            str(exc),
            extra={"traceback": traceback.format_exc(), "correlation_id": correlation_id},
        )
        return _build_error_response(500, "internal_error", "An unexpected error occurred", correlation_id)


def register_error_handlers(app: FastAPI) -> None:
    """Register exception handlers and middleware on the FastAPI app."""

    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", None)
        logger.warning(
            "AppException handler: %s",
            exc.detail,
            extra={"status_code": exc.status_code, "correlation_id": correlation_id},
        )
        return _build_error_response(exc.status_code, exc.error, exc.detail, correlation_id)

    @app.exception_handler(ValueError)
    async def handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", None)
        logger.warning("ValueError: %s", str(exc), extra={"correlation_id": correlation_id})
        return _build_error_response(422, "validation_error", str(exc), correlation_id)

    @app.exception_handler(Exception)
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        correlation_id = getattr(request.state, "correlation_id", None)
        logger.error(
            "Unhandled exception handler: %s",
            str(exc),
            extra={"traceback": traceback.format_exc(), "correlation_id": correlation_id},
        )
        return _build_error_response(500, "internal_error", "An unexpected error occurred", correlation_id)

    app.add_middleware(BaseHTTPMiddleware, dispatch=error_handler_middleware)
