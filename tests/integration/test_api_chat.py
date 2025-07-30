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

def test_chat_unauthenticated(client):
    resp = client.post("/chat", json={"message": "Hello!"})
    assert resp.status_code == 401
    assert "Authentication required" in resp.json()["detail"]

def test_chat_empty_message(client):
    token = get_token(client)
    resp = client.post("/chat", json={"message": "   "}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"]

def test_chat_too_long(client):
    token = get_token(client)
    long_message = "a" * 4097
    resp = client.post("/chat", json={"message": long_message}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
    assert "too long" in resp.json()["detail"]
