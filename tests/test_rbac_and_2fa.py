import pyotp


async def _register_and_login(client, email: str, password: str = "supersecret123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login_resp = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    return login_resp.json()["access_token"]


async def test_non_admin_cannot_list_users(client):
    token = await _register_and_login(client, "regular@example.com")
    resp = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


async def test_2fa_setup_and_login_flow(client):
    token = await _register_and_login(client, "twofa@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    setup_resp = await client.post("/api/v1/auth/2fa/setup", headers=headers)
    assert setup_resp.status_code == 200
    secret = setup_resp.json()["secret"]

    code = pyotp.TOTP(secret).now()
    enable_resp = await client.post("/api/v1/auth/2fa/enable", json={"code": code}, headers=headers)
    assert enable_resp.status_code == 200
    assert enable_resp.json()["totp_enabled"] is True

    # Login without a TOTP code must now fail.
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "twofa@example.com", "password": "supersecret123"},
    )
    assert login_resp.status_code == 401

    # Login with a fresh valid TOTP code succeeds.
    fresh_code = pyotp.TOTP(secret).now()
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "twofa@example.com",
            "password": "supersecret123",
            "totp_code": fresh_code,
        },
    )
    assert login_resp.status_code == 200
