"""Enable/disable trading strategies per user (persisted in TradingConfig)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.dependencies import get_current_user
from backend.app.schemas.strategy import StrategyResponse, StrategyToggleRequest
from database.models.user import User
from database.repositories.trading_config_repository import TradingConfigRepository
from database.session import get_db
from strategies.registry import ALL_STRATEGIES

router = APIRouter(prefix="/strategies", tags=["strategies"])


@router.get("", response_model=list[StrategyResponse])
async def list_strategies(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[StrategyResponse]:
    config = await TradingConfigRepository(db).get_or_create_for_user(current_user.id)
    enabled = config.enabled_strategies or {}
    return [StrategyResponse(name=name, enabled=enabled.get(name, True)) for name in ALL_STRATEGIES]


@router.patch("/{strategy_name}", response_model=StrategyResponse)
async def toggle_strategy(
    strategy_name: str,
    payload: StrategyToggleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StrategyResponse:
    if strategy_name not in ALL_STRATEGIES:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown strategy")

    config = await TradingConfigRepository(db).get_or_create_for_user(current_user.id)
    enabled_strategies = dict(config.enabled_strategies or {})
    enabled_strategies[strategy_name] = payload.enabled
    config.enabled_strategies = enabled_strategies
    await db.flush()

    return StrategyResponse(name=strategy_name, enabled=payload.enabled)
