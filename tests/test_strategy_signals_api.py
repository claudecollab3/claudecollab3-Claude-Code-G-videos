async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return login_resp.json()["access_token"]


async def test_list_strategies_defaults_to_all_enabled(client):
    token = await _register_and_login(client, "strat1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/strategies", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 4
    assert all(s["enabled"] for s in body)


async def test_toggle_strategy_persists(client):
    token = await _register_and_login(client, "strat2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    toggle_resp = await client.patch(
        "/api/v1/strategies/trend_following", json={"enabled": False}, headers=headers
    )
    assert toggle_resp.status_code == 200
    assert toggle_resp.json()["enabled"] is False

    list_resp = await client.get("/api/v1/strategies", headers=headers)
    strategies = {s["name"]: s["enabled"] for s in list_resp.json()}
    assert strategies["trend_following"] is False
    assert strategies["mean_reversion"] is True


async def test_toggle_unknown_strategy_404s(client):
    token = await _register_and_login(client, "strat3@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.patch(
        "/api/v1/strategies/not_a_real_strategy", json={"enabled": False}, headers=headers
    )
    assert resp.status_code == 404


async def test_evaluate_signals_with_no_market_data_returns_empty_list(client):
    token = await _register_and_login(client, "strat4@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/signals/evaluate",
        json={
            "symbol": "EURUSD",
            "timeframes": ["M15", "H1", "H4"],
            "account": {
                "balance": 1000.0,
                "equity": 1000.0,
                "starting_balance_today": 1000.0,
                "starting_balance_this_week": 1000.0,
                "peak_equity": 1000.0,
            },
        },
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_evaluate_signals_after_sync_returns_valid_shape_when_signals_fire(client):
    token = await _register_and_login(client, "strat5@example.com")
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
            "count": 300,
        },
        headers=headers,
    )

    resp = await client.post(
        "/api/v1/signals/evaluate",
        json={
            "symbol": "EURUSD",
            "timeframes": ["M15", "H1", "H4"],
            "account": {
                "balance": 1000.0,
                "equity": 1000.0,
                "starting_balance_today": 1000.0,
                "starting_balance_this_week": 1000.0,
                "peak_equity": 1000.0,
            },
        },
        headers=headers,
    )
    assert resp.status_code == 200
    for entry in resp.json():
        assert entry["direction"] in ("long", "short")
        assert "risk_decision" in entry
        assert set(entry["risk_decision"]) == {"approved", "reason", "volume", "risk_amount"}
