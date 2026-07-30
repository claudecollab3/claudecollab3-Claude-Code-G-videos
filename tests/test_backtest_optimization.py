from datetime import UTC, datetime, timedelta

from backtesting.engine import BacktestResult, BacktestTrade
from backtesting.optimization import grid_search
from strategies.base import Direction

_START = datetime(2026, 1, 1, tzinfo=UTC)


def _result_with_equity(values: list[float], *, trade_count: int = 0) -> BacktestResult:
    equity_curve = [(_START + timedelta(days=i), v) for i, v in enumerate(values)]
    trades = [
        BacktestTrade(
            strategy_name="test",
            symbol="EURUSD",
            direction=Direction.LONG,
            entry_time=_START,
            entry_price=1.1,
            exit_time=_START,
            exit_price=1.1,
            stop_loss=1.09,
            take_profit=1.12,
            volume=1.0,
            pnl=1.0,
            r_multiple=1.0,
            exit_reason="take_profit",
        )
        for _ in range(trade_count)
    ]
    return BacktestResult(
        trades=trades,
        equity_curve=equity_curve,
        starting_balance=values[0],
        ending_balance=values[-1],
    )


def test_grid_search_ranks_by_default_sharpe_objective():
    def strategy_factory(period: int):
        return {"period": period}

    def run_backtest(strategy):
        if strategy["period"] == 20:
            return _result_with_equity([1000, 1050, 1100, 1150, 1200])  # steady uptrend
        return _result_with_equity([1000, 990, 1010, 985, 1000])  # choppy, near-flat

    results = grid_search(
        strategy_factory=strategy_factory,
        parameter_grid={"period": [10, 20]},
        run_backtest=run_backtest,
    )

    assert results[0].parameters == {"period": 20}
    assert results[0].report.sharpe_ratio > results[1].report.sharpe_ratio


def test_grid_search_covers_full_cartesian_product():
    def strategy_factory(period: int, threshold: float):
        return {"period": period, "threshold": threshold}

    def run_backtest(strategy):
        return _result_with_equity([1000, 1000 + strategy["period"] + strategy["threshold"]])

    results = grid_search(
        strategy_factory=strategy_factory,
        parameter_grid={"period": [10, 20], "threshold": [0.1, 0.2]},
        run_backtest=run_backtest,
    )

    assert len(results) == 4
    parameter_sets = {(r.parameters["period"], r.parameters["threshold"]) for r in results}
    assert parameter_sets == {(10, 0.1), (10, 0.2), (20, 0.1), (20, 0.2)}


def test_grid_search_respects_custom_objective():
    def strategy_factory(name: str):
        return {"name": name}

    def run_backtest(strategy):
        # "many_trades" has the worse equity curve but more trades; a
        # total_trades objective should still rank it first, proving the
        # custom objective (not the default Sharpe) drove the ranking.
        if strategy["name"] == "many_trades":
            return _result_with_equity([1000, 990, 980], trade_count=10)
        return _result_with_equity([1000, 1100, 1200], trade_count=1)

    results = grid_search(
        strategy_factory=strategy_factory,
        parameter_grid={"name": ["many_trades", "few_trades"]},
        run_backtest=run_backtest,
        objective=lambda report: report.total_trades,
    )

    assert results[0].parameters == {"name": "many_trades"}
