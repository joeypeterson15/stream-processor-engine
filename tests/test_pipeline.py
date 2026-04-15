import time

from fastapi.testclient import TestClient

from stream_engine.server import create_app


def test_post_event_requires_event_id():
    app = create_app()
    with TestClient(app) as client:
        resp = client.post("/event", json={"payload": {"x": 1}})
        assert resp.status_code == 422


def test_clicks_and_orders_handlers_write_state():
    app = create_app()
    with TestClient(app) as client:
        now = time.time()

        click_resp = client.post(
            "/event",
            json={
                "event_id": 1,
                "payload": {
                    "timestamp": now,
                    "prod_id": "p1",
                    "session_id": "s1",
                    "user_id": "u1",
                },
            },
        )
        assert click_resp.status_code == 200
        assert click_resp.json()["ok"] is True
        assert click_resp.json()["event_id"] == 1

        orders_resp = client.post(
            "/event",
            json={
                "event_id": 2,
                "payload": {
                    "timestamp": now,
                    "prod_id": "p9",
                },
            },
        )
        assert orders_resp.status_code == 200

        clicks_state = client.get("/stream-store/state/clicks")
        assert clicks_state.status_code == 200
        clicks_json = clicks_state.json()
        assert "clicks:by_user" in clicks_json
        assert "clicks:global" in clicks_json

        orders_state = client.get("/stream-store/state/orders")
        assert orders_state.status_code == 200
        orders_json = orders_state.json()
        assert "orders:by_product" in orders_json
        assert "orders:global" in orders_json


def test_websocket_broadcasts_to_all_connections_on_write():
    app = create_app()
    with TestClient(app) as client:
        with client.websocket_connect("/stream-store/ws") as ws1, client.websocket_connect(
            "/stream-store/ws"
        ) as ws2:
            # initial state snapshots
            ws1.receive_json()
            ws2.receive_json()

            now = time.time()
            resp = client.post(
                "/event",
                json={
                    "event_id": 1,
                    "payload": {
                        "timestamp": now,
                        "prod_id": "p1",
                        "session_id": "s1",
                        "user_id": "u1",
                    },
                },
            )
            assert resp.status_code == 200

            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()

            assert "clicks:by_user" in msg1
            assert "clicks:global" in msg1
            assert msg1 == msg2

