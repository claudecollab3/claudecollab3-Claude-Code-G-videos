# Architecture

## Goals

The system's purpose is not to maximize trade frequency but to maximize
**risk-adjusted, compounding returns** by trading only high-probability,
multi-confirmation setups, while enforcing hard capital-protection limits
that no strategy or AI signal is allowed to override.

## High-level data flow

```
┌──────────────┐    ┌────────────────────┐    ┌───────────────────────┐
│ Broker (MT5/ │───▶│ Market Data         │───▶│ Feature Store          │
│ MT4) + News  │    │ Ingestion Service   │    │ (M1..D1 OHLCV, ticks,  │
│ Providers    │    │ (async, WebSocket)  │    │  spread, session data) │
└──────────────┘    └────────────────────┘    └───────────┬───────────┘
                                                            │
                     ┌──────────────────────────────────────┼───────────────┐
                     ▼                                      ▼               ▼
             ┌───────────────┐                    ┌──────────────┐  ┌──────────────┐
             │ Strategy       │                    │ AI Ensemble  │  │ News Engine   │
             │ Engine (SMC/   │                    │ Engine        │  │ (calendar,    │
             │ ICT, indicators│                    │ (ML/DL/RL/    │  │  impact,      │
             │ , S/R, FVG...) │                    │  Bayesian/    │  │  blackout      │
             └───────┬───────┘                    │  Transformer) │  │  windows)     │
                     │                              └──────┬───────┘  └──────┬───────┘
                     └───────────────┬──────────────────────┴─────────────────┘
                                     ▼
                          ┌───────────────────────┐
                          │ Decision & Confidence  │
                          │ Engine (weighted        │
                          │ consensus + filter      │
                          │ checklist → 0-100%)     │
                          └───────────┬───────────┘
                                      ▼
                          ┌───────────────────────┐
                          │ Risk Manager           │
                          │ (position sizing,      │
                          │  drawdown/loss limits,  │
                          │  exposure caps)         │
                          └───────────┬───────────┘
                                      ▼
                          ┌───────────────────────┐
                          │ Execution Engine        │
                          │ (broker adapter,        │
                          │  retries, latency log)  │
                          └───────────┬───────────┘
                                      ▼
                          ┌───────────────────────┐
                          │ PostgreSQL + Redis      │
                          │ (trades, signals, audit)│
                          └───────────┬───────────┘
                                      ▼
                     ┌────────────────────────────────┐
                     │ Dashboard (WebSocket) + Alerts  │
                     │ (Telegram/Discord/Email/Push)   │
                     └────────────────────────────────┘
```

## Module responsibilities

| Module | Responsibility |
|---|---|
| `broker/` | Talks to MT5 (via the official Python package) and MT4 (via a bridge/EA + ZeroMQ or file/socket bridge). Normalizes both into a common `BrokerAdapter` interface: quotes, account info, order placement/modification, position/order streams, reconnect-with-backoff. |
| `database/` | SQLAlchemy async models + Alembic migrations for trades, signals, market data, news, predictions, performance, configs, logs, users, sessions, audit trail. Single source of truth; every other module reads/writes through repositories here, never raw SQL scattered around. |
| `strategies/` | Each strategy implements a common `Strategy` interface (`analyze(context) -> Signal | None`) so strategies are independently enable/disable-able and testable. SMC/ICT concepts (BOS, CHoCH, order blocks, FVG, liquidity sweeps, kill zones) live as reusable detectors under `strategies/smc/` shared across strategies. |
| `ai/` | Feature engineering + an ensemble of independently-trained models (gradient boosted trees, LSTM/time-series, transformer, Bayesian, RL agent). Each model outputs a directional probability; the ensemble combines them via weighted voting (weights tuned from historical performance, not fixed forever). |
| `risk/` | Enforces per-trade risk %, daily/weekly/monthly loss and drawdown limits, max concurrent positions, max lot size, spread/slippage ceilings. This is the **one place** allowed to veto or resize a trade — strategy/AI confidence never bypasses it. |
| `execution/` | Translates an approved, risk-sized order into broker calls with retry-on-transient-error, latency logging, and SL/TP/trailing/partial-close management post-entry. |
| `authentication/` | JWT auth, 2FA (TOTP), RBAC, encrypted broker-credential vault (Fernet/AES-GCM with keys from a secrets manager, never plaintext). |
| `notifications/` | Fan-out dispatcher for Telegram/Discord/email/push/desktop events (trade opened/closed, news warnings, drawdown alerts, disconnects). |
| `backtesting/` | Replays historical data through the same strategy/AI/risk code paths used live (no parallel "backtest-only" logic) to avoid train/live skew, and reports win rate, profit factor, Sharpe/Sortino, drawdown, expectancy, equity curve. |
| `training/` | Offline, isolated from production inference — trains/retrains models on historical MT5/MT4/CSV/tick data and only promotes a model to production after it passes a validation gate. |
| `monitoring/` | Health checks, structured logs, metrics (latency, execution slippage, model drift) exposed for Prometheus/Grafana-style scraping. |

## Design principles

1. **One code path for backtest and live.** Strategies, AI inference, and
   risk checks are never duplicated between backtest and live execution —
   only the data source and the (paper vs. real) broker adapter differ.
2. **Risk manager is the final gate.** Every order passes through it
   immediately before execution, regardless of which strategy or model
   produced it.
3. **Confidence is a first-class signal property.** Every `Signal` object
   carries a `confidence: float (0-100)` plus the breakdown of which
   filters passed/failed, so decisions are explainable, not a black box.
4. **Secrets never touch the database in plaintext.** Broker passwords,
   API keys, and investor passwords are encrypted at rest and decrypted
   only in-memory at the point of use.
5. **Everything is configurable, nothing is hardcoded.** Risk limits,
   strategy toggles, confidence thresholds, and account-size profiles are
   all driven by the `config/` layer and per-user settings in the DB, not
   constants buried in code.

## Technology stack

- **API**: Python 3.11+, FastAPI, AsyncIO, WebSockets (live dashboard + broker streams)
- **Data**: PostgreSQL (system of record), Redis (cache, pub/sub, rate limiting)
- **Compute**: NumPy, Pandas, Polars for vectorized analysis; ONNX Runtime for portable low-latency inference; optional GPU acceleration for training
- **Frontend**: React + TypeScript + Vite, WebSocket live updates
- **Packaging**: Docker Compose for local/dev, Kubernetes manifests for production (Phase 8)

## Account-size aware position sizing

The risk module treats account size as a first-class input, not an
afterthought: below a broker's minimum viable lot/margin requirements, the
system refuses to size a "real" trade and instead surfaces a clear warning
("this account is too small to trade this instrument safely at your current
risk %") rather than silently forcing an oversized position.
