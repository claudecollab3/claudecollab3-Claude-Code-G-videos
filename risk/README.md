# risk/

Risk management. This is the one module allowed to veto or resize any trade
regardless of strategy/AI confidence.

## Implemented in Phase 4

```
risk/
  limits.py          AccountState, RiskLimits, and the daily/weekly loss,
                     drawdown, and profit-percent calculations
  position_sizing.py Risk-per-trade -> lot size, with a broker minimum-lot/
                     account-size viability check (returns a clear warning
                     instead of silently forcing an oversized trade)
  guards.py          Spread/slippage ceilings, break-even and trailing-stop
                     calculations, partial-close volume helper
  manager.py         RiskManager.evaluate() — the single approve/reject gate:
                     emergency stop -> confidence threshold -> spread ->
                     open-position/trade-count caps -> daily/weekly loss ->
                     drawdown -> position sizing. Every rejection carries a
                     human-readable reason.
```

`RiskManager` is what `execution/engine.py` requires before it will place an
order — a `Signal`, however high its confidence, is only ever a *candidate*
until this gate approves it.

## Not yet built

`targets.py` (stop-after-daily/weekly/monthly-target behavior) — the
underlying `daily_profit_percent()` calculation already exists in
`limits.py`; only the "then what" policy (e.g. auto-pause trading) remains.
