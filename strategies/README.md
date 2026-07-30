# strategies/

Pluggable trading strategies, built out in **Phase 4**. `base.py` defines the
shared `Strategy` interface, `MarketContext`, and `Signal` types used by every
strategy and by the AI ensemble in Phase 5.

Planned strategy modules:

```
strategies/
  base.py             Strategy ABC, MarketContext, Signal (Phase 1 - done)
  smc/                Smart Money Concepts / ICT detectors: BOS, CHoCH,
                      order blocks, fair value gaps, liquidity sweeps,
                      kill zones, session opens
  price_action.py     Support/resistance, supply/demand, candlestick patterns
  indicators.py       EMA/SMA crossovers, RSI, MACD, ATR, ADX, Bollinger
                      Bands, Ichimoku, SuperTrend, VWAP
  trend_following.py
  scalping.py
  swing.py
  breakout.py
  reversal.py
  mean_reversion.py
  grid.py             Optional, disabled by default
  martingale.py       Disabled by default; requires explicit opt-in + warning
  registry.py         Enable/disable + weighting configuration per strategy
```

Each strategy is independently toggleable via `config/` and per-user settings
so a user can run e.g. only "Trend Following + SMC" while leaving scalping
and grid/martingale off.
