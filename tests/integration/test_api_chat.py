
# Standard library imports

# Third-party imports

# Local application imports
from app.core.auth import create_access_token
import app.api.chat

def get_token(client):
    client.post("/users/register", json={
        "name": "Chat User",
        "email": "chatuser@example.com",
        "password": "Password1!"
    })
    resp = client.post("/users/login", json={
        "email": "chatuser@example.com",
        "password": "Password1!"
    })
    return resp.json()["access_token"]

def test_chat_happy_path(client):
    token = get_token(client)
    resp = client.post("/chat", json={"message": "Hello!"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "response" in resp.json()

def test_chat_non_hello_message(client):
    token = get_token(client)
    resp = client.post("/chat", json={"message": "How are you?"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["response"].startswith("I'm here to help!")

def test_chat_unauthenticated(client):
    resp = client.post("/chat", json={"message": "Hello!"})
    assert resp.status_code == 401
    # FastAPI default message for missing/invalid Bearer token
    assert resp.json()["detail"] == "Not authenticated"

def test_chat_invalid_token(client):
    # Malformed token
    resp = client.post("/chat", json={"message": "Hello!"}, headers={"Authorization": "Bearer invalid.token.value"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Authentication required. Please log in or register."

def test_chat_token_missing_sub(client, monkeypatch):
    token = create_access_token({"foo": "bar"})  # no 'sub'
    resp = client.post("/chat", json={"message": "Hello!"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Authentication required. Please log in or register."

def test_chat_token_nonexistent_user(client, monkeypatch):
    token = create_access_token({"sub": "ghost@example.com"})
    resp = client.post("/chat", json={"message": "Hello!"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Authentication required. Please log in or register."


import pytest

@pytest.mark.parametrize("payload,expected_error", [
    ( {"message": "   "}, "empty" ),
    ( {"message": "a" * 4097}, "too long" ),
    ( {}, None ),
    ( {"message": 12345}, None ),
])
def test_chat_invalid_cases(client, payload, expected_error):
    token = get_token(client)
    resp = client.post("/chat", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422
    if expected_error:
        assert any(expected_error in err["msg"].lower() for err in resp.json().get("detail", []))

# Simulate service/database error by monkeypatching the chat service (example, adjust as needed)
def test_chat_service_exception(client, monkeypatch):
    token = get_token(client)
    def raise_exception(*args, **kwargs):
        raise Exception("Simulated service failure")
    monkeypatch.setattr(app.api.chat, "process_chat", raise_exception)
    import pytest
    with pytest.raises(Exception) as excinfo:
        client.post("/chat", json={"message": "Hello!"}, headers={"Authorization": f"Bearer {token}"})
    assert "Simulated service failure" in str(excinfo.value)
