import random
import time
from datetime import UTC, datetime, timedelta

from backtesting.engine import BacktestConfig, BacktestEngine
from database.models.market_data import Candle, Timeframe
from risk.limits import RiskLimits
from strategies.base import Direction, MarketContext, Signal, Strategy
from strategies.registry import ALL_STRATEGIES

_START = datetime(2026, 1, 1, tzinfo=UTC)


def _candles_from_ohlc(rows: list[tuple[float, float, float, float]]) -> list[Candle]:
    return [
        Candle(
            symbol="EURUSD",
            timeframe=Timeframe.H1,
            timestamp=_START + timedelta(hours=i),
            open=o,
            high=h,
            low=low_,
            close=c,
            volume=100.0,
        )
        for i, (o, h, low_, c) in enumerate(rows)
    ]


def _flat_row(price: float = 1.1000, spread: float = 0.0005) -> tuple[float, float, float, float]:
    return (price, price + spread, price - spread, price)


class _OnceStrategy(Strategy):
    """Fires exactly one LONG signal, on the bar where the primary
    timeframe's visible history reaches `fire_at_bar_count` bars -- giving
    tests full control over exactly when/where a trade opens."""

    name = "once"

    def __init__(
        self,
        *,
        fire_at_bar_count: int,
        stop_loss: float,
        take_profit: float,
        confidence: float = 100.0,
    ):
        self.fire_at_bar_count = fire_at_bar_count
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.confidence = confidence
        self._fired = False

    def analyze(self, context: MarketContext) -> Signal | None:
        h1 = context.timeframes.get("H1")
        if h1 is None or self._fired or len(h1) != self.fire_at_bar_count:
            return None
        self._fired = True
        return Signal(
            strategy_name=self.name,
            symbol=context.symbol,
            direction=Direction.LONG,
            entry_price=float(h1["close"].iloc[-1]),
            stop_loss=self.stop_loss,
            take_profit=self.take_profit,
            confidence=self.confidence,
        )


def _default_limits(**overrides) -> RiskLimits:
    defaults = dict(
        risk_per_trade_percent=1.0,
        max_daily_loss_percent=50.0,
        max_weekly_loss_percent=50.0,
        max_drawdown_percent=50.0,
        max_open_positions=3,
        max_trades_per_day=10,
        max_spread_points=30.0,
        max_slippage_points=10.0,
        daily_profit_target_percent=100.0,
        confidence_threshold=90.0,
    )
    defaults.update(overrides)
    return RiskLimits(**defaults)  # type: ignore[arg-type]


def _run(strategy: Strategy, rows: list[tuple[float, float, float, float]], **config_overrides):
    candles = _candles_from_ohlc(rows)
    config = BacktestConfig(
        symbol="EURUSD",
        primary_timeframe=Timeframe.H1,
        risk_limits=config_overrides.pop("risk_limits", _default_limits()),
        min_history_bars=60,
        **config_overrides,
    )
    engine = BacktestEngine(strategies=[strategy], config=config)
    return engine.run({Timeframe.H1: candles})


def test_stop_loss_exit():
    rows = [_flat_row()] * 61 + [(1.0995, 1.0996, 1.0980, 1.0985)]
    strategy = _OnceStrategy(fire_at_bar_count=61, stop_loss=1.0990, take_profit=1.1050)

    result = _run(strategy, rows)

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "stop_loss"
    assert trade.exit_price == 1.0990
    assert trade.pnl < 0
    assert result.ending_balance == result.starting_balance + trade.pnl
    assert len(result.equity_curve) == 2  # bars 60 (entry) and 61 (exit)


def test_take_profit_exit():
    rows = [_flat_row()] * 61 + [(1.1005, 1.1060, 1.1000, 1.1055)]
    strategy = _OnceStrategy(fire_at_bar_count=61, stop_loss=1.0950, take_profit=1.1050)

    result = _run(strategy, rows)

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "take_profit"
    assert trade.exit_price == 1.1050
    assert trade.pnl > 0


def test_end_of_data_closes_open_position():
    rows = [_flat_row()] * 66  # never breaches SL/TP, which are set far away
    strategy = _OnceStrategy(fire_at_bar_count=61, stop_loss=1.0900, take_profit=1.1200)

    result = _run(strategy, rows)

    assert len(result.trades) == 1
    trade = result.trades[0]
    assert trade.exit_reason == "end_of_data"
    assert trade.pnl == 0  # flat price throughout
    assert len(result.equity_curve) == (66 - 60) + 1  # +1 for the final forced-close point


def test_low_confidence_signal_is_rejected_and_never_opens():
    rows = [_flat_row()] * 65
    strategy = _OnceStrategy(
        fire_at_bar_count=61, stop_loss=1.0900, take_profit=1.1200, confidence=50.0
    )

    result = _run(strategy, rows, risk_limits=_default_limits(confidence_threshold=90.0))

    assert result.trades == []
    assert result.rejected_signal_count == 1
    assert result.ending_balance == result.starting_balance


def test_max_open_positions_rejects_second_signal_in_same_bar():
    rows = [_flat_row()] * 65
    strategy_a = _OnceStrategy(fire_at_bar_count=61, stop_loss=1.0900, take_profit=1.1200)
    strategy_b = _OnceStrategy(fire_at_bar_count=61, stop_loss=1.0900, take_profit=1.1200)

    config = BacktestConfig(
        symbol="EURUSD",
        primary_timeframe=Timeframe.H1,
        risk_limits=_default_limits(max_open_positions=1),
        min_history_bars=60,
    )
    engine = BacktestEngine(strategies=[strategy_a, strategy_b], config=config)
    candles = _candles_from_ohlc(rows)
    result = engine.run({Timeframe.H1: candles})

    # Both strategies fire in the same bar; only one position may open.
    assert result.rejected_signal_count == 1
    assert len(result.trades) == 1


def test_insufficient_history_returns_empty_result():
    rows = [_flat_row()] * 10  # fewer bars than min_history_bars
    strategy = _OnceStrategy(fire_at_bar_count=5, stop_loss=1.09, take_profit=1.12)
    result = _run(strategy, rows)
    assert result.trades == []
    assert result.equity_curve == []
    assert result.ending_balance == result.starting_balance


def test_full_replay_completes_quickly_with_all_strategies():
    """Regression guard: an earlier version re-sliced the entire history
    and re-ran full SMC structure/order-block/FVG detection from scratch on
    every bar, which was O(n^2) and hung the server on a realistic dataset
    (see backtesting/README.md). 400 bars x all registered strategies
    should complete in low single-digit seconds; a reintroduced per-bar
    quadratic cost would blow past this bound by orders of magnitude."""
    random.seed(0)
    rows = []
    price = 1.1000
    for _ in range(400):
        o = price
        c = price + random.uniform(-0.001, 0.001)
        h = max(o, c) + random.uniform(0, 0.0005)
        low_ = min(o, c) - random.uniform(0, 0.0005)
        rows.append((o, h, low_, c))
        price = c

    engine = BacktestEngine(
        strategies=[cls() for cls in ALL_STRATEGIES.values()],
        config=BacktestConfig(
            symbol="EURUSD",
            primary_timeframe=Timeframe.H1,
            risk_limits=_default_limits(confidence_threshold=50.0),
        ),
    )
    start = time.monotonic()
    engine.run({Timeframe.H1: _candles_from_ohlc(rows)})
    assert time.monotonic() - start < 15.0
