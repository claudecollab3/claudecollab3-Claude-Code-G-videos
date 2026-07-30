async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return login_resp.json()["access_token"]


async def test_default_preferences_have_desktop_enabled(client):
    token = await _register_and_login(client, "notif1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/notifications/preferences", headers=headers)
    assert resp.status_code == 200
    channels = resp.json()["channels"]
    assert channels["desktop"] is True
    assert channels["telegram"] is False


async def test_update_preferences_persists(client):
    token = await _register_and_login(client, "notif2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.patch(
        "/api/v1/notifications/preferences",
        json={"channel": "discord", "enabled": True},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["channels"]["discord"] is True

    get_resp = await client.get("/api/v1/notifications/preferences", headers=headers)
    assert get_resp.json()["channels"]["discord"] is True


async def test_send_test_notification_delivers_via_desktop_by_default(client):
    token = await _register_and_login(client, "notif3@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/notifications/test",
        json={"event": "trade_opened", "title": "Hello", "body": "World"},
        headers=headers,
    )
    assert resp.status_code == 200
    results = resp.json()
    desktop_result = next(r for r in results if r["channel"] == "desktop")
    assert desktop_result["success"] is True


async def test_notification_history_reflects_test_dispatch(client):
    token = await _register_and_login(client, "notif4@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/notifications/test",
        json={"event": "trading_paused", "title": "Paused", "body": "High-impact news"},
        headers=headers,
    )

    resp = await client.get("/api/v1/notifications/history", headers=headers)
    assert resp.status_code == 200
    events = [entry["event"] for entry in resp.json()]
    assert "trading_paused" in events


async def test_preferences_require_auth(client):
    resp = await client.get("/api/v1/notifications/preferences")
    assert resp.status_code == 401
