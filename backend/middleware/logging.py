"""Request/response logging middleware with correlation IDs."""

import time
import uuid
from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from utils.logger import get_logger

logger = get_logger(__name__)

_correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


def get_correlation_id() -> str:
    """Return the current request's correlation ID."""
    return _correlation_id_ctx.get()


async def logging_middleware(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Log request/response details with a correlation ID."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    _correlation_id_ctx.set(correlation_id)

    # Attach to request state so other middleware/handlers can access it
    request.state.correlation_id = correlation_id

    method = request.method
    path = request.url.path
    client = request.client.host if request.client else "unknown"

    logger.info(
        "Request started",
        extra={
            "correlation_id": correlation_id,
            "method": method,
            "path": path,
            "client": client,
            "query": str(request.query_params),
        },
    )

    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    response.headers["X-Correlation-ID"] = correlation_id

    logger.info(
        "Request completed",
        extra={
            "correlation_id": correlation_id,
            "method": method,
            "path": path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )

    return response
