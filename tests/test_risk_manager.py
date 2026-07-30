from risk.limits import AccountState, RiskLimits
from risk.manager import RiskManager
from strategies.base import Direction, Signal


def _limits(**overrides) -> RiskLimits:
    defaults = dict(
        risk_per_trade_percent=1.0,
        max_daily_loss_percent=3.0,
        max_weekly_loss_percent=6.0,
        max_drawdown_percent=10.0,
        max_open_positions=3,
        max_trades_per_day=10,
        max_spread_points=30.0,
        max_slippage_points=10.0,
        daily_profit_target_percent=2.0,
        confidence_threshold=90.0,
    )
    defaults.update(overrides)
    return RiskLimits(**defaults)  # type: ignore[arg-type]


def _account(**overrides) -> AccountState:
    defaults = dict(
        balance=1000.0,
        equity=1000.0,
        starting_balance_today=1000.0,
        starting_balance_this_week=1000.0,
        peak_equity=1000.0,
    )
    defaults.update(overrides)
    return AccountState(**defaults)  # type: ignore[arg-type]


def _signal(**overrides) -> Signal:
    defaults = dict(
        strategy_name="test",
        symbol="EURUSD",
        direction=Direction.LONG,
        entry_price=1.1000,
        stop_loss=1.0950,
        take_profit=1.1100,
        confidence=95.0,
    )
    defaults.update(overrides)
    return Signal(**defaults)  # type: ignore[arg-type]


def test_approved_trade_returns_sized_volume():
    manager = RiskManager(_limits())
    decision = manager.evaluate(signal=_signal(), account=_account(), current_spread_points=10.0)
    assert decision.approved
    assert decision.volume > 0


def test_rejects_when_emergency_stop_active():
    manager = RiskManager(_limits())
    decision = manager.evaluate(
        signal=_signal(), account=_account(emergency_stop=True), current_spread_points=10.0
    )
    assert not decision.approved
    assert "Emergency stop" in decision.reason


def test_rejects_below_confidence_threshold():
    manager = RiskManager(_limits(confidence_threshold=90.0))
    decision = manager.evaluate(
        signal=_signal(confidence=80.0), account=_account(), current_spread_points=10.0
    )
    assert not decision.approved
    assert "Confidence" in decision.reason


def test_rejects_when_spread_too_wide():
    manager = RiskManager(_limits(max_spread_points=20.0))
    decision = manager.evaluate(signal=_signal(), account=_account(), current_spread_points=25.0)
    assert not decision.approved
    assert "Spread" in decision.reason


def test_rejects_when_max_open_positions_reached():
    manager = RiskManager(_limits(max_open_positions=2))
    decision = manager.evaluate(
        signal=_signal(), account=_account(open_positions_count=2), current_spread_points=10.0
    )
    assert not decision.approved
    assert "open positions" in decision.reason


def test_rejects_when_max_trades_per_day_reached():
    manager = RiskManager(_limits(max_trades_per_day=5))
    decision = manager.evaluate(
        signal=_signal(), account=_account(trades_today=5), current_spread_points=10.0
    )
    assert not decision.approved
    assert "trades per day" in decision.reason


def test_rejects_when_daily_loss_limit_hit():
    manager = RiskManager(_limits(max_daily_loss_percent=3.0))
    decision = manager.evaluate(
        signal=_signal(),
        account=_account(equity=960.0, starting_balance_today=1000.0),  # -4%
        current_spread_points=10.0,
    )
    assert not decision.approved
    assert "Daily loss" in decision.reason


def test_rejects_when_drawdown_limit_hit():
    manager = RiskManager(_limits(max_drawdown_percent=10.0))
    decision = manager.evaluate(
        signal=_signal(),
        # Isolate drawdown: today's/this week's starting balance equals
        # current equity, so only the peak-equity drawdown check trips.
        account=_account(
            equity=880.0,
            starting_balance_today=880.0,
            starting_balance_this_week=880.0,
            peak_equity=1000.0,  # -12% from peak
        ),
        current_spread_points=10.0,
    )
    assert not decision.approved
    assert "drawdown" in decision.reason


def test_rejects_when_position_size_not_viable():
    manager = RiskManager(_limits())
    # Isolate sizing: balance/equity/starting-balances/peak all equal so no
    # loss or drawdown check trips before the sizing check is reached.
    decision = manager.evaluate(
        signal=_signal(),
        account=_account(
            balance=1.0,
            equity=1.0,
            starting_balance_today=1.0,
            starting_balance_this_week=1.0,
            peak_equity=1.0,
        ),
        current_spread_points=10.0,
    )
    assert not decision.approved
    assert "too small" in decision.reason
