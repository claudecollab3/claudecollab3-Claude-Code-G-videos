# execution/

Order execution engine, built out in **Phase 3/4**. Takes a risk-approved
order and talks to a `BrokerAdapter` (see `broker/`) to place/manage it.

Planned structure:

```
execution/
  engine.py         open/modify/close/partial-close, move SL/TP, trail stop,
                    cancel pending orders
  retry.py          Retry-on-transient-error policy (tenacity-based)
  latency.py        Execution latency + broker response logging
```

The engine is broker-agnostic: it depends only on the `BrokerAdapter`
interface from `broker/`, so the same execution logic runs against MT5, MT4,
paper trading, and backtesting fills.
