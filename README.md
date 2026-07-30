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
cp .env.example .env            # fill in secrets / broker credentials
docker compose up -d postgres redis
pip install -r requirements.txt -r requirements-dev.txt
uvicorn backend.app.main:app --reload
```

Health check: `GET http://localhost:8000/api/v1/health`

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap / Phases](docs/ROADMAP.md)
- [Disclaimer & Risk Notice](docs/DISCLAIMER.md)
