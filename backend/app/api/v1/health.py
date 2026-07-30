"""Liveness/readiness endpoints used by orchestration and uptime monitoring."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from database.session import get_db

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app_name: str
    app_env: str
    trading_mode: str


class ReadinessResponse(HealthResponse):
    database: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        app_env=settings.app_env.value,
        trading_mode=settings.trading_mode.value,
    )


@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness(db: AsyncSession = Depends(get_db)) -> ReadinessResponse:
    base = await health()

    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:  # pragma: no cover - depends on live DB
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {exc}",
        ) from exc

    return ReadinessResponse(**base.model_dump(), database=db_status)
