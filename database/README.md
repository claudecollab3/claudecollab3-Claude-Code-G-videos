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
