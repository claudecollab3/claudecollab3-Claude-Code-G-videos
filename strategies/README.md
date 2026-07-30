# strategies/

Pluggable trading strategies. `base.py` defines the shared `Strategy`
interface, `MarketContext`, and `Signal` types used by every strategy and
(in Phase 5) by the AI ensemble.

## Implemented in Phase 4

```
strategies/
  base.py             Strategy ABC, MarketContext, Signal
  data.py             Candle (ORM) -> pandas DataFrame conversion
  indicators.py       EMA, SMA, RSI, MACD, ATR, Bollinger Bands, ADX,
                      SuperTrend, VWAP, Ichimoku
  market_conditions.py Volume spikes, volatility percentile, spread
                      widening, a coarse manipulation/stop-hunt heuristic
  smc/
    structure.py      Swing points, Break of Structure (BOS) / Change of
                      Character (CHoCH) detection
    order_blocks.py   Order block (supply/demand zone) detection
    fair_value_gap.py Fair Value Gap (FVG) detection
    liquidity.py      Liquidity sweep detection
    levels.py         Support/Resistance clustering from swing points
    sessions.py       Trading sessions + London/New York kill zones
  trend_following.py  EMA(50)/EMA(200) crossover + ADX + H1/H4 alignment
  mean_reversion.py   Bollinger Band extreme + RSI confirmation
  breakout.py         S/R level break + volume-spike confirmation
  smc_strategy.py     BOS/CHoCH + order block/FVG confluence + kill zone
  registry.py         Enable/disable per user's TradingConfig, runs all
                      enabled strategies against a MarketContext, isolates
                      a failing strategy so it can't take down the others
```

Exposed via `GET /api/v1/strategies` (list + enabled state) and
`PATCH /api/v1/strategies/{name}` (toggle), persisted per-user in
`TradingConfig.enabled_strategies`. `POST /api/v1/signals/evaluate` runs the
registry against persisted OHLCV data for a symbol and returns every
candidate `Signal` alongside the risk manager's decision (see `risk/`).

BOS/CHoCH is an inherently discretionary SMC/ICT concept with no single
canonical algorithm; `smc/structure.py` documents the simplified heuristic
used here (fractal swing pivots + same-direction/opposite-direction
breaks) rather than presenting it as *the* official definition.

## Not yet built

`scalping.py`, `swing.py`, `reversal.py`, `grid.py`, `martingale.py`
(grid/martingale disabled-by-default per the spec) — straightforward to add
on top of the same `Strategy`/`MarketContext`/indicator building blocks
already in place.
