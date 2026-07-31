#!/bin/sh
# Applies pending Alembic migrations before the API starts serving traffic.
# Safe to run on every container start: Alembic is a no-op once the schema
# is already at head, so this works for both the first boot and every
# subsequent deploy/restart.
set -e

# Managed platforms (e.g. Render) assign the listen port via $PORT and
# route traffic to it; default to 8000 for docker-compose / local use.
: "${PORT:=8000}"

alembic upgrade head
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "$PORT"
