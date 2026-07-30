async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return login_resp.json()["access_token"]


async def test_upcoming_events_defaults_to_empty_without_provider_configured(client):
    resp = await client.get("/api/v1/news/upcoming")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_news_policy_defaults_to_trade_without_provider_configured(client):
    token = await _register_and_login(client, "news1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/news/policy", json={"symbol": "EURUSD"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["action"] == "trade"
    assert body["upcoming_event"] is None


async def test_news_policy_requires_auth(client):
    resp = await client.post("/api/v1/news/policy", json={"symbol": "EURUSD"})
    assert resp.status_code == 401
