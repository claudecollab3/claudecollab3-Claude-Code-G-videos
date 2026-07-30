# Security notes

## Hardening done in Phase 8

- **Fail-fast production guard** (`config.settings.Settings.
  assert_production_ready()`, called at app startup): refuses to boot with
  `APP_ENV=production` if `JWT_SECRET_KEY` is missing, short, or still the
  dev-only default, or if `CREDENTIAL_ENCRYPTION_KEY` is unset. Before this,
  a misconfigured production deployment would boot normally and sign JWTs
  with a value hardcoded in this public source tree.
- **Debug mode forced off in production** regardless of the `APP_DEBUG` env
  var, so unhandled exceptions can't leak stack traces to clients.
- **Security response headers** (`backend/app/main.py`): `X-Content-Type-
  Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`,
  and `Strict-Transport-Security` in production.
- **Dependency vulnerabilities fixed** (found via `pip-audit`): swapped
  `python-jose` for `PyJWT` (we only ever use HS256; python-jose pulls in
  `ecdsa`/`rsa`/`pyasn1` unconditionally for algorithms we never use, and
  the specific `ecdsa` CVE it dragged in has no upstream fix), and bumped
  `cryptography`, `lightgbm`, `python-dotenv`, and `fastapi` (which pulls a
  patched-enough `starlette`) to CVE-fixed versions. Verified with a full
  clean-venv install + the entire test suite passing before pinning.
- Rate limiting on `/auth/login` (5/60s) and `/auth/register` (5/300s) —
  Redis-backed, so it holds across multiple backend replicas — predates
  this phase (Phase 2) but is noted here as it's directly relevant.
- Refresh tokens are opaque and only ever persisted as a SHA-256 hash
  (Phase 2); broker credentials are Fernet-encrypted at rest (Phase 2).

## Known residual findings (accepted for this session, not silently ignored)

- **`starlette` CVEs requiring `fastapi>=0.116`**: our `fastapi==0.115.14`
  pin resolves `starlette` up to `<0.47.0`, which fixes several but not all
  CVEs flagged by `pip-audit` (the remainder need `starlette>=0.47.1` or a
  `1.x` release). Jumping ~26 minor versions of FastAPI in one pass without
  the ability to regression-test that scope thoroughly was judged too risky
  for this session; tracked as follow-up.
- **npm `esbuild` dev-server CVE** (`GHSA-67mh-4wv8-2f99`, moderate): only
  exploitable against a *running local Vite dev server* (a malicious website
  reading responses via CORS) — it does not affect the production build,
  which is static files served by `docker/nginx.conf`, no dev server
  involved. The fix requires Vite 8 (breaking major version); not applied
  here for the same reason as above.
- **Dev tooling CVEs** (`black`, `pytest`, `setuptools` — flagged by
  `pip-audit --local` against the dev venv): these are build/test-time
  tools, never shipped in the deployed backend image, so they carry no
  production exposure. Left at their current pins.
- **`strategies/smc/liquidity.py`**: not a CVE, but flagged during Phase 8
  performance profiling — see `strategies/README.md`. Not on any current
  request path, so not fixed here, but would need the same vectorization
  treatment as its siblings before being wired into a live strategy.

## Reporting

This is a demo/portfolio project, not a monitored production service —
there's no dedicated security contact. If you fork this for real trading
with real capital, treat the items above as your starting checklist, not
a clean bill of health.
