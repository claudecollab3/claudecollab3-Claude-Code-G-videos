# backtesting/

Backtest engine and performance analytics, built out in **Phase 6**.

```
backtesting/
  engine.py         Replays historical bars through the same strategies/,
                    ai/, and risk/ code used live (no parallel backtest-only
                    logic), producing simulated fills via a paper-style
                    broker adapter
  metrics.py        Win rate, profit factor, Sharpe, Sortino, max drawdown,
                    average win/loss, expectancy
  reports.py        Equity curve, monthly/yearly returns, heatmaps
  optimization.py   Parameter sweeps / walk-forward optimization
```
