"""Runs the strategy engine + risk manager against persisted market data for
a symbol, returning every candidate signal alongside the risk manager's
approve/reject decision (and sized volume, if approved).

Note: `account` is supplied by the caller rather than computed from a live
trade ledger — a running Trade/PnL history table lands with the execution
loop in a later phase. This still exercises the full strategy -> risk
pipeline end-to-end against real persisted OHLCV data.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.dependencies import get_current_user
from backend.app.schemas.signals import EvaluateSignalsRequest, RiskDecisionResponse, SignalResponse
from database.models.user import User
from database.repositories.market_data_repository import MarketDataRepository
from database.repositories.trading_config_repository import TradingConfigRepository
from database.session import get_db
from risk.limits import AccountState, RiskLimits
from risk.manager import RiskManager
from strategies.base import MarketContext
from strategies.data import candles_to_dataframe
from strategies.registry import StrategyRegistry

router = APIRouter(prefix="/signals", tags=["signals"])


@router.post("/evaluate", response_model=list[SignalResponse])
async def evaluate_signals(
    payload: EvaluateSignalsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SignalResponse]:
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
    signals = StrategyRegistry(config.enabled_strategies).run_all(context)

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
    for signal in signals:
        decision = risk_manager.evaluate(
            signal=signal, account=account, current_spread_points=payload.current_spread_points
        )
        responses.append(
            SignalResponse(
                strategy_name=signal.strategy_name,
                symbol=signal.symbol,
                direction=signal.direction.value,
                entry_price=signal.entry_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                confidence=signal.confidence,
                reasons=signal.reasons,
                risk_decision=RiskDecisionResponse(
                    approved=decision.approved,
                    reason=decision.reason,
                    volume=decision.volume,
                    risk_amount=decision.risk_amount,
                ),
            )
        )
    return responses
