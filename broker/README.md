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

## Implemented in Phase 3

- `adapter.py` — the `BrokerAdapter` interface plus shared dataclasses
  (`AccountInfo`, `Quote`, `CandleData`, `OrderRequest`/`OrderResult`, `Position`).
- `paper.py` — a fully working in-memory `PaperBrokerAdapter` (simulated
  fills/positions), usable today for demo trading and as the default for
  `BrokerType.PAPER` credentials.
- `mt5/adapter.py` — a real `MT5BrokerAdapter` against the official
  `MetaTrader5` package (import deferred to `connect()`; blocking calls
  offloaded via `asyncio.to_thread`). Only actually connects on a
  Windows host with a running MT5 terminal.
- `mt4/adapter.py` — a real `MT4BrokerAdapter` speaking a DWX-style
  ZeroMQ request/response protocol to a bridge EA. Only actually connects
  against a running MT4 terminal + EA.
- `factory.py` — builds the right adapter for a `BrokerCredential` row,
  decrypting its secret via `authentication.vault`.
- `credentials.py` — secret encrypt/decrypt helpers + `connect_with_backoff`
  (tenacity-based exponential backoff retry, used for both initial connect
  and reconnect-after-drop).
- `instruments.py` — the default supported instrument catalog (Gold,
  Bitcoin, major Forex pairs, indices, crypto pairs).
- `ingestion.py` — `MarketDataIngestionService` pulls OHLCV bars across
  M1–D1 from a connected adapter and upserts them via
  `database.repositories.market_data_repository`.

Exposed via `POST/GET/DELETE /api/v1/broker/credentials`,
`POST /api/v1/broker/credentials/{id}/connect` (test-connects and returns
account info), `GET /api/v1/broker/instruments`,
`GET /api/v1/market-data/candles`, and `POST /api/v1/market-data/sync`.

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
