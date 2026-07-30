async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return login_resp.json()["access_token"]


async def test_list_instruments_includes_gold_and_bitcoin(client):
    resp = await client.get("/api/v1/broker/instruments")
    assert resp.status_code == 200
    symbols = {i["symbol"] for i in resp.json()}
    assert "XAUUSD" in symbols
    assert "BTCUSD" in symbols


async def test_create_credential_never_exposes_password(client):
    token = await _register_and_login(client, "broker1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/broker/credentials",
        json={
            "broker_type": "paper",
            "broker_name": "Paper Demo",
            "server": "demo",
            "login": "demo-login",
            "password": "super-secret-broker-password",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "password" not in body
    assert body["broker_type"] == "paper"

    list_resp = await client.get("/api/v1/broker/credentials", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1


async def test_connect_paper_credential_returns_account_info(client):
    token = await _register_and_login(client, "broker2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/broker/credentials",
        json={"broker_type": "paper", "broker_name": "Paper Demo"},
        headers=headers,
    )
    credential_id = create_resp.json()["id"]

    connect_resp = await client.post(
        f"/api/v1/broker/credentials/{credential_id}/connect", headers=headers
    )
    assert connect_resp.status_code == 200
    assert connect_resp.json()["currency"] == "USD"


async def test_sync_and_read_candles(client):
    token = await _register_and_login(client, "broker3@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/broker/credentials",
        json={"broker_type": "paper", "broker_name": "Paper Demo"},
        headers=headers,
    )
    credential_id = create_resp.json()["id"]

    sync_resp = await client.post(
        "/api/v1/market-data/sync",
        json={
            "broker_credential_id": credential_id,
            "symbol": "EURUSD",
            "timeframes": ["M1", "M5"],
            "count": 25,
        },
        headers=headers,
    )
    assert sync_resp.status_code == 200
    assert sync_resp.json() == {"M1": 25, "M5": 25}

    candles_resp = await client.get(
        "/api/v1/market-data/candles", params={"symbol": "EURUSD", "timeframe": "M1"}
    )
    assert candles_resp.status_code == 200
    assert len(candles_resp.json()) == 25


async def test_delete_credential(client):
    token = await _register_and_login(client, "broker4@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/broker/credentials",
        json={"broker_type": "paper", "broker_name": "Paper Demo"},
        headers=headers,
    )
    credential_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/v1/broker/credentials/{credential_id}", headers=headers
    )
    assert delete_resp.status_code == 204

    list_resp = await client.get("/api/v1/broker/credentials", headers=headers)
    assert list_resp.json() == []
