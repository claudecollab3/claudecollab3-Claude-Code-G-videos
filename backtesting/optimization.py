"""Parameter-sweep optimization: runs a backtest per parameter combination
and ranks results by a chosen objective metric (default: Sharpe ratio)."""

from collections.abc import Callable
from dataclasses import dataclass
from itertools import product
from typing import Any

from backtesting.metrics import PerformanceReport, compute_performance_report
from strategies.base import Strategy


def _default_objective(report: PerformanceReport) -> float:
    return report.sharpe_ratio or 0.0


@dataclass
class OptimizationResult:
    parameters: dict[str, Any]
    report: PerformanceReport


def grid_search(
    *,
    strategy_factory: Callable[..., Strategy],
    parameter_grid: dict[str, list[Any]],
    run_backtest: Callable[[Strategy], Any],
    objective: Callable[[PerformanceReport], float] = _default_objective,
) -> list[OptimizationResult]:
    """`run_backtest` builds and runs a `BacktestEngine` for a single
    strategy instance (with a fixed `BacktestConfig`/historical data) and
    returns its `BacktestResult`. Kept as a caller-supplied callback rather
    than baked in here so this module doesn't need to know how the caller
    sources historical data or wires up risk limits."""
    keys = list(parameter_grid.keys())
    results = []

    for values in product(*parameter_grid.values()):
        parameters = dict(zip(keys, values, strict=False))
        strategy = strategy_factory(**parameters)
        backtest_result = run_backtest(strategy)
        report = compute_performance_report(backtest_result)
        results.append(OptimizationResult(parameters=parameters, report=report))

    return sorted(results, key=lambda r: objective(r.report), reverse=True)
