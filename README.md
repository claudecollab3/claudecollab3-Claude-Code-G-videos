# Trading Bot — AI Forex & Crypto Trading System

A production-grade, AI-driven trading platform for MT4/MT5 covering Forex,
Gold (XAU/USD), Bitcoin (BTC/USD), major indices, and crypto pairs. The system
analyzes markets continuously across multiple timeframes, combines an
ensemble of AI models with classical technical/Smart-Money-Concepts analysis,
scores every potential trade with a 0–100% confidence rating, and only acts
on signals that clear a configurable threshold — with risk management and
capital preservation as first-class citizens, not an afterthought.

> **Disclaimer:** Trading forex, crypto, and CFDs carries substantial risk of
> loss. This system is a decision-support and automation tool, not a
> guarantee of profit. No AI system can predict markets with certainty. Use
> demo/paper trading extensively before risking real capital, and never risk
> money you cannot afford to lose. See [docs/DISCLAIMER.md](docs/DISCLAIMER.md).

## Project status

Built iteratively in 8 phases (see [docs/ROADMAP.md](docs/ROADMAP.md)).
Currently: **Phase 1 — Architecture & Scaffolding**.

## Repository layout

```
backend/          FastAPI application: API routes, services, dependency wiring
frontend/         Web dashboard (React + TypeScript + Vite)
ai/               AI decision engine: ensemble models, feature engineering, inference
strategies/       Pluggable trading strategies (SMC/ICT, price action, indicators)
risk/             Risk management: position sizing, drawdown guards, limits
execution/        Order execution engine: open/modify/close, retries, latency logging
broker/           Broker adapters (MT5, MT4) and credential handling
database/         SQLAlchemy models, Alembic migrations, repositories
authentication/   JWT auth, 2FA, RBAC, encrypted credential vault
notifications/    Telegram, Discord, email, push, desktop notification dispatch
training/         Offline model training pipelines (isolated from production)
backtesting/      Backtest engine, performance analytics, optimization
monitoring/       Health checks, metrics, structured logging, alerting
docker/           Dockerfiles and container orchestration
tests/            Unit and integration tests
docs/             Architecture, API, deployment, and user documentation
config/           Centralized settings and environment configuration
```

## Quick start (development)

```bash
cp .env.example .env             # fill in secrets / broker credentials
python -c "from authentication.vault import Vault; print(Vault.generate_key())"  # -> CREDENTIAL_ENCRYPTION_KEY
docker compose up -d postgres redis
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head              # create the database schema
uvicorn backend.app.main:app --reload
```

Health check: `GET http://localhost:8000/api/v1/health`
Readiness (checks DB connectivity): `GET http://localhost:8000/api/v1/health/ready`

## Authentication

- `POST /api/v1/auth/register`, `/login`, `/refresh`, `/logout`
- `POST /api/v1/auth/2fa/setup`, `/2fa/enable`, `/2fa/disable`
- `GET/PATCH /api/v1/users/me`, `GET /api/v1/users` (admin only)

Access tokens are short-lived JWTs; refresh tokens are opaque, rotated on
every use, and stored only as a SHA-256 hash (see `authentication/jwt.py`).
Broker credentials and other secrets are encrypted at rest via
`authentication/vault.py` (Fernet) — never stored in plaintext.

## Broker connectivity & market data

- `POST/GET/DELETE /api/v1/broker/credentials` — store an encrypted MT5/MT4/paper login
- `POST /api/v1/broker/credentials/{id}/connect` — test-connect, returns account info
- `GET /api/v1/broker/instruments` — default Forex/Gold/Bitcoin/index/crypto catalog
- `GET /api/v1/market-data/candles?symbol=EURUSD&timeframe=M5` — read persisted OHLCV
- `POST /api/v1/market-data/sync` — pull fresh bars from a connected broker into the DB

MT5 requires a Windows host with a running terminal (the official
`MetaTrader5` package is Windows-only); MT4 requires a bridge EA speaking
the ZeroMQ protocol in `broker/mt4/adapter.py`. Neither is reachable from
this dev/CI environment — use a `paper` broker credential to exercise the
full connect → sync → candle-read flow without live broker infrastructure.

## Strategies, risk, and signal evaluation

- `GET /api/v1/strategies` / `PATCH /api/v1/strategies/{name}` — list/toggle
  per-user strategy enablement (trend-following, mean-reversion, breakout, SMC)
- `POST /api/v1/signals/evaluate` — runs enabled strategies against persisted
  OHLCV data for a symbol and returns each candidate signal alongside the
  risk manager's approve/reject decision and sized volume

Every signal passes through `risk.manager.RiskManager` before it could ever
be executed: confidence threshold, spread, open-position/trade-count caps,
daily/weekly loss, drawdown, and position-size viability, in that order —
see `risk/README.md`. `execution/engine.py` is what actually places an
approved order via a `BrokerAdapter`.

## AI prediction, news engine, and the Decision & Confidence Engine

- `POST /api/v1/ai/predict` — runs the model ensemble (XGBoost, LightGBM,
  Gaussian Naive Bayes, a small neural net, a contextual-bandit RL agent,
  and a deterministic momentum baseline) against persisted OHLCV data and
  persists an `AIPrediction`
- `GET /api/v1/news/upcoming` / `POST /api/v1/news/policy` — economic
  calendar lookup and the pre-trade Trade/Wait/Reduce-risk/Close-existing
  decision (no calendar vendor is wired in by default — see `ai/README.md`)
- `POST /api/v1/decision/evaluate` — the full pipeline in one call:
  strategies → AI ensemble confirmation → news policy → risk manager,
  returning each confirmed signal with a pass/fail checklist

See `ai/README.md` for the honest scope notes on what's a lightweight
stand-in here (e.g. no PyTorch/TensorFlow-based LSTM/Transformer, no deep
RL) versus what's a real, working implementation behind the same interface.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap / Phases](docs/ROADMAP.md)
- [Disclaimer & Risk Notice](docs/DISCLAIMER.md)
