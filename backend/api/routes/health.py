"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    timestamp: str
    database: str
    version: str = "1.0.0"


@router.get("/health", response_model=HealthResponse)
async def get_health(
    db: AsyncSession = Depends(get_async_session),
) -> HealthResponse:
    """Check API and database health."""
    now = datetime.now(timezone.utc).isoformat()
    db_status = "unhealthy"

    try:
        result = await db.execute(text("SELECT 1"))
        if result.scalar_one() == 1:
            db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    overall = "healthy" if db_status == "healthy" else "degraded"

    return HealthResponse(
        status=overall,
        timestamp=now,
        database=db_status,
        version="1.0.0",
    )
