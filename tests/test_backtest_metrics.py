from datetime import UTC, datetime, timedelta

import pytest

from backtesting.engine import BacktestResult, BacktestTrade
from backtesting.metrics import compute_performance_report
from strategies.base import Direction

_START = datetime(2026, 1, 15, tzinfo=UTC)


def _trade(pnl: float, *, days_offset: int) -> BacktestTrade:
    ts = _START + timedelta(days=days_offset)
    return BacktestTrade(
        strategy_name="test",
        symbol="EURUSD",
        direction=Direction.LONG,
        entry_time=ts,
        entry_price=1.1,
        exit_time=ts,
        exit_price=1.1 + pnl / 1000,
        stop_loss=1.09,
        take_profit=1.12,
        volume=1.0,
        pnl=pnl,
        r_multiple=pnl / 10,
        exit_reason="take_profit" if pnl > 0 else "stop_loss",
    )


def test_performance_report_basic_math():
    trades = [
        _trade(100.0, days_offset=0),
        _trade(50.0, days_offset=1),
        _trade(-40.0, days_offset=2),
    ]
    equity_curve = [
        (_START, 1000.0),
        (_START + timedelta(days=1), 1100.0),
        (_START + timedelta(days=2), 1150.0),
        (_START + timedelta(days=3), 1110.0),
    ]
    result = BacktestResult(
        trades=trades, equity_curve=equity_curve, starting_balance=1000.0, ending_balance=1110.0
    )

    report = compute_performance_report(result)

    assert report.total_trades == 3
    assert report.win_rate == pytest.approx(200 / 3)
    assert report.profit_factor == pytest.approx(150 / 40)
    assert report.average_win == pytest.approx(75.0)
    assert report.average_loss == pytest.approx(40.0)
    assert report.expectancy == pytest.approx((2 / 3) * 75.0 - (1 / 3) * 40.0)
    assert report.max_drawdown_percent == pytest.approx((1150 - 1110) / 1150 * 100)


def test_performance_report_no_trades():
    result = BacktestResult(
        trades=[], equity_curve=[], starting_balance=1000.0, ending_balance=1000.0
    )
    report = compute_performance_report(result)

    assert report.total_trades == 0
    assert report.win_rate == 0.0
    assert report.profit_factor is None
    assert report.expectancy == 0.0
    assert report.sharpe_ratio is None
    assert report.sortino_ratio is None


def test_performance_report_all_wins_has_no_profit_factor():
    trades = [_trade(10.0, days_offset=0), _trade(20.0, days_offset=1)]
    equity_curve = [(_START, 1000.0), (_START + timedelta(days=1), 1030.0)]
    result = BacktestResult(
        trades=trades, equity_curve=equity_curve, starting_balance=1000.0, ending_balance=1030.0
    )
    report = compute_performance_report(result)

    assert report.win_rate == 100.0
    assert report.profit_factor is None  # no losses to divide by
    assert report.average_loss == 0.0


def test_monthly_and_yearly_returns_bucket_correctly():
    equity_curve = [
        (datetime(2026, 1, 1, tzinfo=UTC), 1000.0),
        (datetime(2026, 1, 15, tzinfo=UTC), 1100.0),
        (datetime(2026, 2, 1, tzinfo=UTC), 1050.0),
        (datetime(2026, 2, 20, tzinfo=UTC), 1200.0),
    ]
    result = BacktestResult(
        trades=[], equity_curve=equity_curve, starting_balance=1000.0, ending_balance=1200.0
    )
    report = compute_performance_report(result)

    assert report.monthly_returns["2026-01"] == pytest.approx((1100 - 1000) / 1000 * 100)
    assert report.monthly_returns["2026-02"] == pytest.approx((1200 - 1050) / 1050 * 100)
    assert report.yearly_returns["2026"] == pytest.approx((1200 - 1000) / 1000 * 100)
