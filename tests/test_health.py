async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "trading-bot"


async def test_readiness(client):
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
