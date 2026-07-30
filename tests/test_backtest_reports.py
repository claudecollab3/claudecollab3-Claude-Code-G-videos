from datetime import UTC, datetime

from backtesting.engine import BacktestResult, BacktestTrade
from backtesting.reports import (
    equity_curve_report,
    monthly_returns_table,
    pnl_heatmap_by_weekday_hour,
)
from strategies.base import Direction


def _trade(pnl: float, exit_time: datetime) -> BacktestTrade:
    return BacktestTrade(
        strategy_name="test",
        symbol="EURUSD",
        direction=Direction.LONG,
        entry_time=exit_time,
        entry_price=1.1,
        exit_time=exit_time,
        exit_price=1.1,
        stop_loss=1.09,
        take_profit=1.12,
        volume=1.0,
        pnl=pnl,
        r_multiple=0.0,
        exit_reason="take_profit",
    )


def test_equity_curve_report_uses_iso_timestamps():
    ts = datetime(2026, 1, 1, 12, 30, tzinfo=UTC)
    result = BacktestResult(
        trades=[], equity_curve=[(ts, 1000.0)], starting_balance=1000.0, ending_balance=1000.0
    )

    report = equity_curve_report(result)

    assert report[0].timestamp == ts.isoformat()
    assert report[0].equity == 1000.0


def test_pnl_heatmap_buckets_by_weekday_and_hour():
    # 2026-01-05 is a Monday.
    trades = [
        _trade(10.0, datetime(2026, 1, 5, 9, tzinfo=UTC)),
        _trade(-5.0, datetime(2026, 1, 5, 9, tzinfo=UTC)),
        _trade(20.0, datetime(2026, 1, 6, 14, tzinfo=UTC)),  # Tuesday
    ]
    result = BacktestResult(
        trades=trades, equity_curve=[], starting_balance=1000.0, ending_balance=1025.0
    )

    heatmap = pnl_heatmap_by_weekday_hour(result)

    assert heatmap["Monday"][9] == 5.0
    assert heatmap["Tuesday"][14] == 20.0


def test_monthly_returns_table_reshapes_into_year_month_grid():
    table = monthly_returns_table({"2026-01": 3.2, "2026-02": -1.1, "2025-12": 4.0})

    assert table["2026"]["01"] == 3.2
    assert table["2026"]["02"] == -1.1
    assert table["2025"]["12"] == 4.0
