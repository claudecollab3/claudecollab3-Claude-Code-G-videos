# risk/

Risk management, built out in **Phase 4**. This is the one module allowed to
veto or resize any trade regardless of strategy/AI confidence.

Planned structure:

```
risk/
  limits.py          Daily/weekly/monthly loss limits, max drawdown,
                      max trades/day, max open positions, emergency stop
  position_sizing.py Risk-per-trade -> lot size, broker minimum-lot/account-
                      size viability checks and warnings
  guards.py          Spread/slippage/leverage ceilings, break-even &
                      trailing-stop rules, partial-close rules
  targets.py         Daily/weekly/monthly profit targets and stop-after-
                      target behavior
```

Every enforced limit is configurable per user/account and every rejection is
logged with a human-readable reason (e.g. "blocked: would exceed daily loss
limit of 3.0%") so decisions are auditable, not silent.
