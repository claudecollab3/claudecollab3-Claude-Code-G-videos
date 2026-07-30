import pytest

from config.settings import AppEnv, Settings


def _settings(**overrides) -> Settings:
    defaults = dict(
        app_env=AppEnv.PRODUCTION, jwt_secret_key="a" * 40, credential_encryption_key="k"
    )
    defaults.update(overrides)
    return Settings(**defaults)  # type: ignore[arg-type]


def test_production_ready_settings_pass():
    _settings().assert_production_ready()


def test_production_rejects_default_jwt_secret():
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        _settings(jwt_secret_key="dev-only-insecure-secret").assert_production_ready()


def test_production_rejects_short_jwt_secret():
    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        _settings(jwt_secret_key="too-short").assert_production_ready()


def test_production_rejects_missing_encryption_key():
    with pytest.raises(RuntimeError, match="CREDENTIAL_ENCRYPTION_KEY"):
        _settings(credential_encryption_key="").assert_production_ready()


def test_development_settings_skip_the_check():
    _settings(
        app_env=AppEnv.DEVELOPMENT,
        jwt_secret_key="dev-only-insecure-secret",
        credential_encryption_key="",
    ).assert_production_ready()


async def test_responses_include_security_headers(client):
    response = await client.get("/api/v1/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
