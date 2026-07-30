# database/

PostgreSQL models and migrations, built out in **Phase 2**.

```
database/
  session.py       Async SQLAlchemy engine/session factory (reads
                    config.get_settings().database_url)
  models/           ORM models: users, sessions, audit_log, trades, signals,
                    market_data, news_events, ai_predictions, performance,
                    configurations, broker_accounts
  repositories/      Query layer other modules use instead of raw SQL
  migrations/        Alembic migration scripts
```

Every other module reads/writes through the `repositories/` layer here —
no module issues raw SQL directly against the database.

## Implemented in Phase 2

- `base.py` / `types.py` — declarative base + a cross-dialect `GUID` type
  (native `UUID` on Postgres, `CHAR(32)` on SQLite so unit tests can run
  against an in-memory SQLite DB without touching Postgres).
- `models/user.py`, `user_session.py`, `audit_log.py`, `broker_credential.py`,
  `trading_config.py` — users, refresh-token sessions, the audit trail,
  encrypted broker credentials, and per-user trading/risk configuration.
- `repositories/` — one repository per model above.
- `migrations/versions/0001_initial_schema.py` — initial Alembic migration
  creating all of the above tables.

## Running migrations

```bash
alembic upgrade head        # apply migrations
alembic revision --autogenerate -m "describe change"   # generate a new one
```

`database/migrations/env.py` reads `DATABASE_URL` from `config.get_settings()`,
so make sure `.env` is populated first.

