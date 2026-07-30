"""Decision & Confidence Engine endpoint: strategies -> AI ensemble
confirmation -> news policy -> risk manager, in one call."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ai.decision import DecisionEngine
from ai.news.factory import get_calendar_provider
from ai.registry import build_default_ensemble
from authentication.dependencies import get_current_user
from backend.app.schemas.decision import (
    ChecklistItemResponse,
    ConfirmedSignalResponse,
    EvaluateDecisionRequest,
)
from backend.app.schemas.signals import RiskDecisionResponse
from database.models.user import User
from database.repositories.market_data_repository import MarketDataRepository
from database.repositories.trading_config_repository import TradingConfigRepository
from database.session import get_db
from risk.limits import AccountState, RiskLimits
from risk.manager import RiskManager
from strategies.base import MarketContext
from strategies.data import candles_to_dataframe
from strategies.registry import StrategyRegistry

router = APIRouter(prefix="/decision", tags=["decision"])

_ensemble = build_default_ensemble()


@router.post("/evaluate", response_model=list[ConfirmedSignalResponse])
async def evaluate_decision(
    payload: EvaluateDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ConfirmedSignalResponse]:
    market_data = MarketDataRepository(db)
    timeframes = {}
    for timeframe in payload.timeframes:
        candles = await market_data.get_latest(
            payload.symbol.upper(), timeframe, limit=payload.candle_limit
        )
        timeframes[timeframe.value] = candles_to_dataframe(candles)

    config = await TradingConfigRepository(db).get_or_create_for_user(current_user.id)

    context = MarketContext(
        symbol=payload.symbol.upper(),
        timeframes=timeframes,
        spread_points=payload.current_spread_points,
    )
    strategy_signals = StrategyRegistry(config.enabled_strategies).run_all(context)

    provider = get_calendar_provider()
    news_events = await provider.upcoming_events(hours_ahead=24)

    engine = DecisionEngine(_ensemble)
    confirmed = engine.evaluate(
        context=context,
        strategy_signals=strategy_signals,
        news_events=news_events,
        news_trading_enabled=config.news_trading_enabled,
        news_blackout_minutes=config.trade_news_blackout_minutes,
        now=datetime.now(UTC),
    )

    limits = RiskLimits(
        risk_per_trade_percent=config.risk_per_trade_percent,
        max_daily_loss_percent=config.max_daily_loss_percent,
        max_weekly_loss_percent=config.max_weekly_loss_percent,
        max_drawdown_percent=config.max_drawdown_percent,
        max_open_positions=config.max_open_positions,
        max_trades_per_day=config.max_trades_per_day,
        max_spread_points=config.max_spread_points,
        max_slippage_points=config.max_slippage_points,
        daily_profit_target_percent=config.daily_profit_target_percent,
        confidence_threshold=config.confidence_threshold,
    )
    risk_manager = RiskManager(limits)
    account = AccountState(
        balance=payload.account.balance,
        equity=payload.account.equity,
        starting_balance_today=payload.account.starting_balance_today,
        starting_balance_this_week=payload.account.starting_balance_this_week,
        peak_equity=payload.account.peak_equity,
        open_positions_count=payload.account.open_positions_count,
        trades_today=payload.account.trades_today,
        emergency_stop=payload.account.emergency_stop,
    )

    responses = []
    for item in confirmed:
        decision = risk_manager.evaluate(
            signal=item.signal, account=account, current_spread_points=payload.current_spread_points
        )
        responses.append(
            ConfirmedSignalResponse(
                strategy_name=item.signal.strategy_name,
                symbol=item.signal.symbol,
                direction=item.signal.direction.value,
                entry_price=item.signal.entry_price,
                stop_loss=item.signal.stop_loss,
                take_profit=item.signal.take_profit,
                confidence=item.signal.confidence,
                reasons=item.signal.reasons,
                checklist=[
                    ChecklistItemResponse(name=c.name, passed=c.passed, detail=c.detail)
                    for c in item.checklist
                ],
                risk_decision=RiskDecisionResponse(
                    approved=decision.approved,
                    reason=decision.reason,
                    volume=decision.volume,
                    risk_amount=decision.risk_amount,
                ),
            )
        )
    return responses
