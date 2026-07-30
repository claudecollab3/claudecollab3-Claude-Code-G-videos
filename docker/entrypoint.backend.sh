#!/bin/sh
# Applies pending Alembic migrations before the API starts serving traffic.
# Safe to run on every container start: Alembic is a no-op once the schema
# is already at head, so this works for both the first boot and every
# subsequent deploy/restart.
set -e

alembic upgrade head
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
