import pytest
from fastapi import status

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
    from app.core.auth import create_access_token
    token = create_access_token({"foo": "bar"})  # no 'sub'
    resp = client.post("/chat", json={"message": "Hello!"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Authentication required. Please log in or register."


def test_chat_token_nonexistent_user(client, monkeypatch):
    from app.core.auth import create_access_token
    token = create_access_token({"sub": "ghost@example.com"})
    resp = client.post("/chat", json={"message": "Hello!"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Authentication required. Please log in or register."


def test_chat_empty_message(client):
    token = get_token(client)
    resp = client.post("/chat", json={"message": "   "}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422
    # Pydantic validation error message is in 'detail' list
    assert any("empty" in err["msg"].lower() for err in resp.json()["detail"])


def test_chat_too_long(client):
    token = get_token(client)
    long_message = "a" * 4097
    resp = client.post("/chat", json={"message": long_message}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422
    assert any("too long" in err["msg"].lower() for err in resp.json()["detail"])
