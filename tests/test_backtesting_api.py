async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return login_resp.json()["access_token"]


async def test_backtest_with_no_market_data_returns_zero_trades(client):
    token = await _register_and_login(client, "backtest1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post("/api/v1/backtesting/run", json={"symbol": "EURUSD"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["performance"]["total_trades"] == 0
    assert body["trades"] == []
    assert body["ending_balance"] == body["starting_balance"]


async def test_backtest_after_sync_returns_valid_shape(client):
    token = await _register_and_login(client, "backtest2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

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
            "symbol": "EURUSD",
            "timeframes": ["M15", "H1", "H4"],
            "count": 500,
        },
        headers=headers,
    )

    resp = await client.post(
        "/api/v1/backtesting/run",
        json={
            "symbol": "EURUSD",
            "primary_timeframe": "H1",
            "auxiliary_timeframes": ["M15", "H4"],
            "candle_limit": 500,
            "starting_balance": 5000.0,
        },
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["starting_balance"] == 5000.0
    assert "sharpe_ratio" in body["performance"]
    assert "monthly_returns" in body["performance"]
    for trade in body["trades"]:
        assert trade["direction"] in ("long", "short")
        assert trade["exit_reason"] in ("stop_loss", "take_profit", "end_of_data")


async def test_backtest_requires_auth(client):
    resp = await client.post("/api/v1/backtesting/run", json={"symbol": "EURUSD"})
    assert resp.status_code == 401
