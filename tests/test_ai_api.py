async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return login_resp.json()["access_token"]


async def _sync_market_data(client, headers, symbol: str = "EURUSD"):
    create_resp = await client.post(
        "/api/v1/broker/credentials",
        json={"broker_type": "paper", "broker_name": "Paper Demo"},
        headers=headers,
    )
    credential_id = create_resp.json()["id"]
    await client.post(
        "/api/v1/market-data/sync",
        json={
            "broker_credential_id": credential_id,
            "symbol": symbol,
            "timeframes": ["M15", "H1", "H4"],
            "count": 300,
        },
        headers=headers,
    )


async def test_predict_with_no_market_data_returns_neutral_ish_result(client):
    token = await _register_and_login(client, "ai1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/ai/predict", json={"symbol": "EURUSD"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["direction"] in ("long", "short")
    assert 0 <= body["confidence"] <= 100
    assert len(body["votes"]) == 6  # timeseries + xgboost + lightgbm + bayesian + neural + rl_agent


async def test_predict_after_sync_returns_valid_shape(client):
    token = await _register_and_login(client, "ai2@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    await _sync_market_data(client, headers)

    resp = await client.post(
        "/api/v1/ai/predict",
        json={"symbol": "EURUSD", "timeframes": ["M15", "H1", "H4"], "candle_limit": 300},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    for vote in body["votes"]:
        assert vote["direction"] in ("long", "short")
        assert 0 <= vote["probability"] <= 1
        assert 0 <= vote["confidence"] <= 100


async def test_predict_requires_auth(client):
    resp = await client.post("/api/v1/ai/predict", json={"symbol": "EURUSD"})
    assert resp.status_code == 401
