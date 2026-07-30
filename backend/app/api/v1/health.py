"""Liveness/readiness endpoints used by orchestration and uptime monitoring."""

from fastapi import APIRouter
from pydantic import BaseModel

from config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    app_name: str
    app_env: str
    trading_mode: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        app_env=settings.app_env.value,
        trading_mode=settings.trading_mode.value,
    )


@router.get("/health/ready", response_model=HealthResponse)
async def readiness() -> HealthResponse:
    # Phase 2+ will extend this to verify DB/Redis/broker connectivity.
    return await health()
