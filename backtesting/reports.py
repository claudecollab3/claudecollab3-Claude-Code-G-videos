"""Equity curve export and heatmap-friendly report structures."""

from collections import defaultdict
from dataclasses import dataclass

from backtesting.engine import BacktestResult


@dataclass
class EquityCurvePoint:
    timestamp: str  # ISO 8601
    equity: float


def equity_curve_report(result: BacktestResult) -> list[EquityCurvePoint]:
    return [
        EquityCurvePoint(timestamp=ts.isoformat(), equity=equity)
        for ts, equity in result.equity_curve
    ]


def pnl_heatmap_by_weekday_hour(result: BacktestResult) -> dict[str, dict[int, float]]:
    """Sum of realized PnL bucketed by (weekday name, hour-of-day) — a
    common way to spot when a strategy actually makes or loses money."""
    buckets: dict[str, dict[int, float]] = defaultdict(lambda: defaultdict(float))
    for trade in result.trades:
        buckets[trade.exit_time.strftime("%A")][trade.exit_time.hour] += trade.pnl
    return {day: dict(hours) for day, hours in buckets.items()}


def monthly_returns_table(monthly_returns: dict[str, float]) -> dict[str, dict[str, float]]:
    """Reshapes {"2026-01": 3.2, "2026-02": -1.1, ...} into
    {"2026": {"01": 3.2, "02": -1.1}, ...} for a year x month heatmap grid."""
    table: dict[str, dict[str, float]] = defaultdict(dict)
    for period, value in monthly_returns.items():
        year, month = period.split("-")
        table[year][month] = value
    return dict(table)
