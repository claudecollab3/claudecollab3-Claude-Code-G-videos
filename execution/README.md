# execution/

Order execution engine. Takes a risk-approved `Signal` + `RiskDecision` and
talks to a `BrokerAdapter` (see `broker/`) to place it.

## Implemented in Phase 4

`engine.py` — `ExecutionEngine.execute(signal, decision)`: refuses to run
against a rejected `RiskDecision`, converts the approved signal + sized
volume into an `OrderRequest`, submits it via the broker adapter with
tenacity-based retry on transient `BrokerConnectionError`s, and records
latency on the returned `OrderResult`.

The engine is broker-agnostic: it depends only on the `BrokerAdapter`
interface from `broker/`, so the same execution logic runs against MT5, MT4,
paper trading, and (Phase 6) backtesting fills.

## Not yet built

Post-entry position management (move SL/TP, trailing stop, partial close,
cancel pending orders) — `risk/guards.py` already has the break-even/
trailing-stop/partial-close *calculations*; wiring them into a live
position-monitoring loop that calls back into the engine is follow-up work.
