async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return login_resp.json()["access_token"]


_ACCOUNT = {
    "balance": 1000.0,
    "equity": 1000.0,
    "starting_balance_today": 1000.0,
    "starting_balance_this_week": 1000.0,
    "peak_equity": 1000.0,
}


async def test_evaluate_decision_with_no_market_data_returns_empty_list(client):
    token = await _register_and_login(client, "decision1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/decision/evaluate",
        json={"symbol": "EURUSD", "account": _ACCOUNT},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_evaluate_decision_after_sync_returns_valid_shape(client):
    token = await _register_and_login(client, "decision2@example.com")
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
        "/api/v1/decision/evaluate",
        json={"symbol": "EURUSD", "account": _ACCOUNT},
        headers=headers,
    )
    assert resp.status_code == 200
    for entry in resp.json():
        assert entry["direction"] in ("long", "short")
        assert {"strategy_confidence", "ai_confirmation", "news"} == {
            c["name"] for c in entry["checklist"]
        }
        assert "risk_decision" in entry


async def test_evaluate_decision_requires_auth(client):
    resp = await client.post(
        "/api/v1/decision/evaluate", json={"symbol": "EURUSD", "account": _ACCOUNT}
    )
    assert resp.status_code == 401
