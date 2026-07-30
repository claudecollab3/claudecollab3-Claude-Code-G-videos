# broker/

Broker adapters, built out in **Phase 3**.

```
broker/
  adapter.py    Common BrokerAdapter interface (quotes, account info, orders,
                positions, streaming) that MT5/MT4/paper all implement
  mt5/          MetaTrader 5 adapter using the official `MetaTrader5` Python
                package. NOTE: that package is Windows-only and must talk to
                a running MT5 terminal, so the MT5 adapter runs inside a
                Windows-hosted worker process; the rest of the stack talks
                to it over the internal API, not by importing it directly.
  mt4/          MetaTrader 4 adapter. MT4 has no official Python API, so this
                bridges to an Expert Advisor running inside MT4 via a
                lightweight ZeroMQ/socket bridge (e.g. DWX/ZeroMQ-connector
                pattern) that exposes the same BrokerAdapter interface.
  paper.py      Paper-trading adapter: simulates fills against live/streamed
                quotes without touching a real account.
  credentials.py Encrypted broker credential storage/retrieval (uses
                authentication/ vault), auto-reconnect with backoff.
```

## Why MT5/MT4 integration is split this way

- MT5's official Python package only runs on Windows and requires a live
  MT5 terminal on the same machine. That constraint is real broker
  infrastructure, not a design choice we can code around — so the adapter is
  isolated behind the common interface, and the worker that hosts it can run
  on a Windows VM/container while the rest of the system stays
  platform-agnostic.
- MT4 has no first-party Python API at all, so an EA + bridge is the
  standard, broker-agnostic way in; the bridge protocol is an implementation
  detail behind the same `BrokerAdapter` interface.
