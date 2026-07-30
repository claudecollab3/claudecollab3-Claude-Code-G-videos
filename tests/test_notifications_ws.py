import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from backend.app.main import app


def test_websocket_rejects_invalid_token():
    # The server closes the connection with a policy-violation code before
    # ever accepting it, for a token that doesn't decode -- the client sees
    # that as a WebSocketDisconnect raised at connect time, not later.
    with TestClient(app) as test_client, pytest.raises(WebSocketDisconnect) as exc_info:
        with test_client.websocket_connect("/api/v1/notifications/ws?token=not-a-real-token"):
            pass
    assert exc_info.value.code == 4401


def test_websocket_forwards_hub_messages_for_valid_token():
    # Deliberately uses only the sync TestClient (for both the HTTP calls
    # and the WebSocket) rather than the async `client` fixture: mixing an
    # async httpx client (running on the pytest-asyncio loop) with
    # TestClient's WebSocket (running on its own portal-managed loop in a
    # separate thread) would hand an `asyncio.Queue` messages from a
    # different event loop than the one that created it.
    with TestClient(app) as test_client:
        test_client.post(
            "/api/v1/auth/register", json={"email": "ws1@example.com", "password": "supersecret123"}
        )
        login_resp = test_client.post(
            "/api/v1/auth/login", json={"email": "ws1@example.com", "password": "supersecret123"}
        )
        token = login_resp.json()["access_token"]

        with test_client.websocket_connect(f"/api/v1/notifications/ws?token={token}") as ws:
            test_resp = test_client.post(
                "/api/v1/notifications/test",
                json={"event": "trade_opened", "title": "Opened", "body": "EURUSD"},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert test_resp.status_code == 200

            received = ws.receive_json()
            assert received["event"] == "trade_opened"
            assert received["title"] == "Opened"
            assert received["body"] == "EURUSD"
