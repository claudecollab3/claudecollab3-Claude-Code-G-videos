import pandas as pd

from strategies.base import MarketContext, Signal, Strategy
from strategies.registry import ALL_STRATEGIES, StrategyRegistry


class _AlwaysSignalsStrategy(Strategy):
    name = "always_signals"

    def analyze(self, context: MarketContext):
        from strategies.base import Direction

        return Signal(
            strategy_name=self.name,
            symbol=context.symbol,
            direction=Direction.LONG,
            entry_price=1.1,
            stop_loss=1.09,
            take_profit=1.12,
            confidence=99.0,
        )


class _BrokenStrategy(Strategy):
    name = "broken"

    def analyze(self, context: MarketContext):
        raise RuntimeError("boom")


def _empty_context() -> MarketContext:
    return MarketContext(symbol="EURUSD", timeframes={}, spread_points=5.0)


def test_registry_respects_enabled_strategies_config():
    registry = StrategyRegistry({name: False for name in ALL_STRATEGIES})
    assert registry.run_all(_empty_context()) == []


def test_registry_default_enables_all_strategies():
    registry = StrategyRegistry(None)
    assert len(registry._strategies) == len(ALL_STRATEGIES)


def test_registry_survives_a_broken_strategy_without_crashing():
    registry = StrategyRegistry({})
    registry._strategies = [_BrokenStrategy(), _AlwaysSignalsStrategy()]
    signals = registry.run_all(_empty_context())
    assert len(signals) == 1
    assert signals[0].strategy_name == "always_signals"


def test_builtin_strategies_return_none_on_insufficient_data():
    registry = StrategyRegistry(None)
    context = MarketContext(
        symbol="EURUSD",
        timeframes={"M15": pd.DataFrame(), "H1": pd.DataFrame(), "H4": pd.DataFrame()},
        spread_points=5.0,
    )
    assert registry.run_all(context) == []
