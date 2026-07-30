"""Backtesting endpoint: replays persisted historical OHLCV data through
the same strategy engine and risk manager used live."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from authentication.dependencies import get_current_user
from backend.app.schemas.backtesting import (
    BacktestRequest,
    BacktestResponse,
    BacktestTradeResponse,
    EquityCurvePointResponse,
    PerformanceReportResponse,
)
from backtesting.engine import BacktestConfig, BacktestEngine
from backtesting.metrics import compute_performance_report
from database.models.user import User
from database.repositories.market_data_repository import MarketDataRepository
from database.repositories.trading_config_repository import TradingConfigRepository
from database.session import get_db
from risk.limits import RiskLimits
from strategies.registry import ALL_STRATEGIES

router = APIRouter(prefix="/backtesting", tags=["backtesting"])


@router.post("/run", response_model=BacktestResponse)
async def run_backtest(
    payload: BacktestRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BacktestResponse:
    config_row = await TradingConfigRepository(db).get_or_create_for_user(current_user.id)
    enabled_strategies = config_row.enabled_strategies or {}
    strategies = [
        cls() for name, cls in ALL_STRATEGIES.items() if enabled_strategies.get(name, True)
    ]

    market_data = MarketDataRepository(db)
    timeframes = [payload.primary_timeframe, *payload.auxiliary_timeframes]
    candles_by_timeframe = {
        tf: await market_data.get_latest(payload.symbol.upper(), tf, limit=payload.candle_limit)
        for tf in timeframes
    }

    risk_limits = RiskLimits(
        risk_per_trade_percent=config_row.risk_per_trade_percent,
        max_daily_loss_percent=config_row.max_daily_loss_percent,
        max_weekly_loss_percent=config_row.max_weekly_loss_percent,
        max_drawdown_percent=config_row.max_drawdown_percent,
        max_open_positions=config_row.max_open_positions,
        max_trades_per_day=config_row.max_trades_per_day,
        max_spread_points=config_row.max_spread_points,
        max_slippage_points=config_row.max_slippage_points,
        daily_profit_target_percent=config_row.daily_profit_target_percent,
        confidence_threshold=config_row.confidence_threshold,
    )

    engine = BacktestEngine(
        strategies=strategies,
        config=BacktestConfig(
            symbol=payload.symbol.upper(),
            primary_timeframe=payload.primary_timeframe,
            risk_limits=risk_limits,
            starting_balance=payload.starting_balance,
            spread_points=payload.spread_points,
            min_history_bars=payload.min_history_bars,
        ),
    )
    result = engine.run(candles_by_timeframe)
    report = compute_performance_report(result)

    return BacktestResponse(
        symbol=payload.symbol.upper(),
        starting_balance=result.starting_balance,
        ending_balance=result.ending_balance,
        rejected_signal_count=result.rejected_signal_count,
        performance=PerformanceReportResponse(
            total_trades=report.total_trades,
            win_rate=report.win_rate,
            profit_factor=report.profit_factor,
            sharpe_ratio=report.sharpe_ratio,
            sortino_ratio=report.sortino_ratio,
            max_drawdown_percent=report.max_drawdown_percent,
            average_win=report.average_win,
            average_loss=report.average_loss,
            expectancy=report.expectancy,
            monthly_returns=report.monthly_returns,
            yearly_returns=report.yearly_returns,
        ),
        equity_curve=[
            EquityCurvePointResponse(timestamp=ts.isoformat(), equity=equity)
            for ts, equity in result.equity_curve
        ],
        trades=[
            BacktestTradeResponse(
                strategy_name=t.strategy_name,
                symbol=t.symbol,
                direction=t.direction.value,
                entry_time=t.entry_time.isoformat(),
                entry_price=t.entry_price,
                exit_time=t.exit_time.isoformat(),
                exit_price=t.exit_price,
                stop_loss=t.stop_loss,
                take_profit=t.take_profit,
                volume=t.volume,
                pnl=t.pnl,
                r_multiple=t.r_multiple,
                exit_reason=t.exit_reason,
            )
            for t in result.trades
        ],
    )
