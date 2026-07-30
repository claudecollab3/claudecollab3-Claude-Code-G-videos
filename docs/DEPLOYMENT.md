# Deployment

## Local / staging (docker-compose)

```bash
cp .env.example .env
python -c "from authentication.vault import Vault; print(Vault.generate_key())"  # -> CREDENTIAL_ENCRYPTION_KEY
python -c "import secrets; print(secrets.token_urlsafe(48))"                     # -> JWT_SECRET_KEY
docker compose up -d --build
```

`docker compose up` builds three images (`docker/Dockerfile.backend`,
`docker/Dockerfile.frontend`) plus Postgres and Redis, and starts them with
the healthcheck-based `depends_on` ordering in `docker-compose.yml`.

- Backend: `docker/entrypoint.backend.sh` runs `alembic upgrade head` before
  starting uvicorn, on every container start. This is idempotent (a no-op
  once the schema is at head), so it's safe on both first boot and every
  subsequent redeploy — no separate manual migration step is needed.
- Frontend: `docker/nginx.conf` serves the built static bundle and reverse
  proxies `/api/` (including the notifications WebSocket) to the backend
  container.

## Production checklist

Set these in the environment (not `.env` committed to a repo — use your
platform's secrets manager):

- `APP_ENV=production` — this is a gate, not just a label:
  - `config.settings.Settings.assert_production_ready()` raises at startup
    if `JWT_SECRET_KEY` is missing/short or still the dev default, or if
    `CREDENTIAL_ENCRYPTION_KEY` is unset. The container refuses to start
    rather than silently serving traffic with a forgeable JWT secret.
  - Forces FastAPI `debug=False` regardless of `APP_DEBUG`, so unhandled
    exceptions never leak stack traces in HTTP responses.
  - CORS `allow_origins` becomes `[]` (same-origin only through the nginx
    reverse proxy) instead of `*`.
- `JWT_SECRET_KEY` — long, random (`secrets.token_urlsafe(48)` or similar).
- `CREDENTIAL_ENCRYPTION_KEY` — from `Vault.generate_key()`. Losing this key
  makes every stored broker credential permanently undecryptable; back it
  up in your secrets manager, not just in `.env`.
- `DATABASE_URL`, `REDIS_URL` pointing at managed/production instances.
- TLS: `docker/nginx.conf` terminates plain HTTP inside the compose network.
  Put a TLS-terminating load balancer or reverse proxy (e.g. a cloud LB, or
  nginx/Caddy with a real certificate) in front of it for real traffic —
  this repo doesn't provision certificates itself.
- Rate limiting on `/auth/login` and `/auth/register` (5 attempts per
  60s/300s respectively) is Redis-backed (`authentication/rate_limit.py`),
  so it works correctly across multiple backend replicas, not just one.

## CI

`.github/workflows/ci.yml` runs two jobs on every push/PR: `backend`
(ruff, black --check, mypy across the whole repo, pytest with coverage) and
`frontend` (`npm ci`, then `npm run build`, which runs `tsc -b` for type
checking before the Vite production build).
