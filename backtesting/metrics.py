"""Performance metrics computed from a completed backtest: win rate, profit
factor, Sharpe/Sortino, max drawdown, average win/loss, expectancy, and
monthly/yearly returns."""

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from backtesting.engine import BacktestResult


@dataclass
class PerformanceReport:
    total_trades: int
    win_rate: float
    profit_factor: float | None
    sharpe_ratio: float | None
    sortino_ratio: float | None
    max_drawdown_percent: float
    average_win: float
    average_loss: float
    expectancy: float
    monthly_returns: dict[str, float]  # "2026-01" -> % return
    yearly_returns: dict[str, float]  # "2026" -> % return


def _bar_returns(equity_curve: list[tuple[datetime, float]]) -> list[float]:
    returns = []
    for (_, e0), (_, e1) in zip(equity_curve, equity_curve[1:], strict=False):
        if e0 != 0:
            returns.append((e1 - e0) / e0)
    return returns


def _sharpe_ratio(returns: list[float]) -> float | None:
    if len(returns) < 2:
        return None
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    std = math.sqrt(variance)
    if std == 0:
        return None
    return mean / std * math.sqrt(len(returns))


def _sortino_ratio(returns: list[float]) -> float | None:
    if len(returns) < 2:
        return None
    mean = sum(returns) / len(returns)
    downside = [min(0.0, r) for r in returns]
    downside_variance = sum(d**2 for d in downside) / len(returns)
    downside_std = math.sqrt(downside_variance)
    if downside_std == 0:
        return None
    return mean / downside_std * math.sqrt(len(returns))


def _max_drawdown_percent(equity_curve: list[tuple[datetime, float]]) -> float:
    peak = float("-inf")
    max_dd = 0.0
    for _, equity in equity_curve:
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, (peak - equity) / peak * 100)
    return max_dd


def _period_returns(equity_curve: list[tuple[datetime, float]], *, fmt: str) -> dict[str, float]:
    buckets: dict[str, list[float]] = defaultdict(list)
    for ts, equity in equity_curve:
        buckets[ts.strftime(fmt)].append(equity)

    returns: dict[str, float] = {}
    for period, equities in buckets.items():
        if equities[0] != 0:
            returns[period] = (equities[-1] - equities[0]) / equities[0] * 100
    return returns


def compute_performance_report(result: BacktestResult) -> PerformanceReport:
    trades = result.trades
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]

    win_rate = (len(wins) / len(trades) * 100) if trades else 0.0
    gross_profit = sum(t.pnl for t in wins)
    gross_loss = abs(sum(t.pnl for t in losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else None

    average_win = (gross_profit / len(wins)) if wins else 0.0
    average_loss = (gross_loss / len(losses)) if losses else 0.0
    win_fraction = win_rate / 100
    expectancy = (
        (win_fraction * average_win) - ((1 - win_fraction) * average_loss) if trades else 0.0
    )

    returns = _bar_returns(result.equity_curve)

    return PerformanceReport(
        total_trades=len(trades),
        win_rate=win_rate,
        profit_factor=profit_factor,
        sharpe_ratio=_sharpe_ratio(returns),
        sortino_ratio=_sortino_ratio(returns),
        max_drawdown_percent=_max_drawdown_percent(result.equity_curve),
        average_win=average_win,
        average_loss=average_loss,
        expectancy=expectancy,
        monthly_returns=_period_returns(result.equity_curve, fmt="%Y-%m"),
        yearly_returns=_period_returns(result.equity_curve, fmt="%Y"),
    )
