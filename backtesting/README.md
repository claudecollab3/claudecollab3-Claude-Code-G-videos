# backtesting/

Backtest engine and performance analytics.

## Implemented in Phase 6

```
backtesting/
  engine.py         BacktestEngine: replays historical Candle rows through
                    the exact same strategies/ (via strategies.registry.
                    run_strategies) and risk/ (RiskManager) code used live —
                    no parallel backtest-only logic. Simulates fills itself
                    bar-by-bar (entries at the signal bar's own close, exits
                    by scanning forward highs/lows against SL/TP, stop-loss
                    assumed to win a same-bar SL+TP tie). See the module
                    docstring for the full list of documented simplifications.
  metrics.py        compute_performance_report(): win rate, profit factor,
                    Sharpe, Sortino, max drawdown, average win/loss,
                    expectancy, monthly/yearly returns
  reports.py        Equity curve export (ISO timestamps), a PnL-by-weekday/
                    hour heatmap, and a year x month returns grid
  optimization.py   grid_search(): runs a backtest per parameter
                    combination and ranks by an objective (default Sharpe)
```

Exposed via `POST /api/v1/backtesting/run` — runs the current user's
enabled strategies (`TradingConfig.enabled_strategies`) and risk limits
against persisted OHLCV history for a symbol, returning the full
performance report, equity curve, and trade list.

AI ensemble confirmation and news-policy gating (Phase 5's `DecisionEngine`)
are not part of the backtest loop yet — it replays `strategies/` + `risk/`
only. Wiring the AI ensemble into the backtest replay (so historical
confidence blending matches what `/decision/evaluate` does live) is natural
follow-up work, not done here.
