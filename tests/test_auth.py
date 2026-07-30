async def test_register_and_login(client):
    register_resp = await client.post(
        "/api/v1/auth/register",
        json={"email": "trader@example.com", "password": "supersecret123"},
    )
    assert register_resp.status_code == 201
    body = register_resp.json()
    assert body["email"] == "trader@example.com"
    assert body["role"] == "trader"

    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "trader@example.com", "password": "supersecret123"},
    )
    assert login_resp.status_code == 200
    tokens = login_resp.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]


async def test_login_wrong_password_rejected(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "trader2@example.com", "password": "supersecret123"},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "trader2@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


async def test_me_with_valid_token(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "trader3@example.com", "password": "supersecret123"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "trader3@example.com", "password": "supersecret123"},
    )
    access_token = login_resp.json()["access_token"]

    me_resp = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "trader3@example.com"


async def test_refresh_rotates_token(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "trader4@example.com", "password": "supersecret123"},
    )
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "trader4@example.com", "password": "supersecret123"},
    )
    old_refresh = login_resp.json()["refresh_token"]

    refresh_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    assert new_tokens["refresh_token"] != old_refresh

    # Old refresh token must be revoked after rotation.
    reuse_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert reuse_resp.status_code == 401
