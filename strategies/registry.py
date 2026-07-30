"""Runs a set of strategies against a MarketContext and collects their
signals. `StrategyRegistry` is what live trading uses (enable/disable
driven by each user's TradingConfig, Phase 2 schema); `run_strategies` is
the underlying function it calls, reused as-is by `backtesting/engine.py`
so backtests exercise identical strategy-execution and fault-isolation
logic to live trading — no parallel "backtest-only" code path.
"""

import structlog

from strategies.base import MarketContext, Signal, Strategy
from strategies.breakout import BreakoutStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.smc_strategy import SmcStrategy
from strategies.trend_following import TrendFollowingStrategy

logger = structlog.get_logger(__name__)

ALL_STRATEGIES: dict[str, type[Strategy]] = {
    "trend_following": TrendFollowingStrategy,
    "mean_reversion": MeanReversionStrategy,
    "breakout": BreakoutStrategy,
    "smc": SmcStrategy,
}


def run_strategies(strategies: list[Strategy], context: MarketContext) -> list[Signal]:
    signals: list[Signal] = []
    for strategy in strategies:
        try:
            signal = strategy.analyze(context)
        except Exception:
            logger.warning(
                "strategy_analysis_failed",
                strategy=strategy.name,
                symbol=context.symbol,
                exc_info=True,
            )
            continue
        if signal is not None:
            signals.append(signal)
    return signals


class StrategyRegistry:
    def __init__(self, enabled_strategies: dict[str, bool] | None = None):
        enabled_strategies = enabled_strategies or {}
        self._strategies: list[Strategy] = [
            cls() for name, cls in ALL_STRATEGIES.items() if enabled_strategies.get(name, True)
        ]

    def run_all(self, context: MarketContext) -> list[Signal]:
        return run_strategies(self._strategies, context)
