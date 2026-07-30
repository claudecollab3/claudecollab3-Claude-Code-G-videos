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

## Performance note (found during Phase 7 manual verification)

Each bar's strategy context is a bounded trailing window
(`BacktestConfig.context_lookback_bars`, default 500), not the full
history-to-date. An earlier version passed `df.loc[:current_time]` — the
*entire* history so far — to every strategy on every bar. Combined with
`strategies.smc.structure.find_swing_points` doing an O(window) scan per
call, that made a full replay O(n^2) in the candle count; against a
realistically-sized synced dataset (2000 candles) it pegged the CPU and
never returned, freezing the whole server (the backtest ran synchronously
in the request handler, blocking the event loop for every other user too).
Fixed by bounding the per-bar window and vectorizing
`find_swing_points` (shift-and-compare instead of a per-bar Python loop
with `.iloc` slicing), and by running `BacktestEngine.run()` via
`asyncio.to_thread` in `backend/app/api/v1/backtesting.py` so a slow
backtest can no longer block the server even if a future strategy
reintroduces expensive per-bar work.
