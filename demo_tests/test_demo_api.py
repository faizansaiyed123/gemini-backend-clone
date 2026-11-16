import time

import pytest
from fastapi.testclient import TestClient

from app.demo_api import DEMO_MOBILE, DEMO_OTP, app, reset_demo_state

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state():
    reset_demo_state()
    yield
    reset_demo_state()


def login() -> str:
    sent = client.post("/auth/send-otp", json={"mobile": DEMO_MOBILE})
    assert sent.status_code == 200
    assert sent.json()["data"]["otp"] == DEMO_OTP
    verified = client.post(
        "/auth/verify-otp",
        json={"mobile": DEMO_MOBILE, "otp": DEMO_OTP},
    )
    assert verified.status_code == 200
    return verified.json()["data"]["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_health_and_seeded_otp_login():
    health = client.get("/health")
    assert health.json() == {"status": "ok", "mode": "demo", "storage": "in-memory"}

    token = login()
    me = client.get("/user/user/me", headers=auth(token))
    assert me.status_code == 200
    assert me.json()["data"]["mobile"] == DEMO_MOBILE
    assert me.json()["data"]["full_name"] == "Avery Morgan"


def test_signup_and_duplicate_mobile_protection():
    payload = {
        "mobile": "9123456789",
        "full_name": "New Demo User",
        "password": "SamplePass123!",
    }
    created = client.post("/auth/signup", json=payload)
    assert created.status_code == 200
    assert created.json()["data"]["token"].startswith("demo-access:")
    duplicate = client.post("/auth/signup", json=payload)
    assert duplicate.status_code == 409


def test_chatroom_create_list_and_detail():
    token = login()
    headers = auth(token)
    created = client.post(
        "/ChatRoom/chatroom",
        headers=headers,
        json={"title": "A new idea"},
    )
    room_id = created.json()["data"]["chatroom_id"]

    listed = client.get("/ChatRoom/chatroom", headers=headers)
    assert any(room["chatroom_id"] == room_id for room in listed.json()["data"])

    detail = client.get(f"/ChatRoom/chatroom/{room_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["name"] == "A new idea"
    assert detail.json()["data"]["messages"] == []


def test_message_is_queued_then_assistant_reply_appears():
    token = login()
    headers = auth(token)
    room_id = "demo-chat-1"

    sent = client.post(
        f"/message/{room_id}/message",
        headers=headers,
        json={"content": "Explain how to structure a Python project"},
    )
    assert sent.status_code == 200
    assert sent.json()["data"]["message_id"]

    before = client.get(f"/ChatRoom/chatroom/{room_id}", headers=headers).json()["data"]
    assert [item["sender"] for item in before["messages"]] == ["user", "ai", "user"]

    time.sleep(0.4)
    after = client.get(f"/ChatRoom/chatroom/{room_id}", headers=headers).json()["data"]
    assert [item["sender"] for item in after["messages"]][-1] == "ai"
    assert "deterministic demo response" in after["messages"][-1]["content"]


def test_basic_daily_limit_and_pro_upgrade():
    token = login()
    headers = auth(token)
    for index in range(5):
        response = client.post(
            "/message/demo-chat-1/message",
            headers=headers,
            json={"content": f"Basic plan message {index + 1}"},
        )
        assert response.status_code == 200

    limited = client.post(
        "/message/demo-chat-1/message",
        headers=headers,
        json={"content": "This should exceed the limit"},
    )
    assert limited.status_code == 429

    upgraded = client.post("/subscribe/pro", headers=headers)
    assert upgraded.status_code == 200
    assert upgraded.json()["data"]["checkout_url"].startswith("http://demo.local")

    for index in range(3):
        response = client.post(
            "/message/demo-chat-1/message",
            headers=headers,
            json={"content": f"Pro plan message {index + 1}"},
        )
        assert response.status_code == 200

    status = client.get("/subscribe/subscription/status", headers=headers)
    assert status.json()["data"]["subscription_tier"] == "pro"


def test_authentication_and_wrong_otp_are_rejected():
    missing_auth = client.get("/user/user/me")
    assert missing_auth.status_code == 401

    client.post("/auth/send-otp", json={"mobile": DEMO_MOBILE})
    wrong_otp = client.post(
        "/auth/verify-otp",
        json={"mobile": DEMO_MOBILE, "otp": "000000"},
    )
    assert wrong_otp.status_code == 400


def test_chatrooms_are_private_to_the_authenticated_user():
    token = login()
    another = client.post(
        "/auth/signup",
        json={
            "mobile": "9987654321",
            "full_name": "Another user",
            "password": "AnotherPass123!",
        },
    ).json()["data"]["token"]
    hidden = client.get(
        "/ChatRoom/chatroom/demo-chat-1",
        headers=auth(another),
    )
    assert hidden.status_code == 404
