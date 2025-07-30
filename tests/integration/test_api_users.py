import pytest
from fastapi import status
from app.schemas.user import UserRegister, UserLogin

def test_register_and_login(client):
    # Register
    resp = client.post("/users/register", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "Password1!"
    })
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["email"] == "testuser@example.com"

    # Duplicate registration
    resp2 = client.post("/users/register", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "Password1!"
    })
    assert resp2.status_code == 400
    assert "already registered" in resp2.json()["detail"]

    # Login
    resp3 = client.post("/users/login", json={
        "email": "testuser@example.com",
        "password": "Password1!"
    })
    assert resp3.status_code == 200
    assert "access_token" in resp3.json()

    # Login wrong password
    resp4 = client.post("/users/login", json={
        "email": "testuser@example.com",
        "password": "WrongPass1!"
    })
    assert resp4.status_code == 401
    assert "incorrect" in resp4.json()["detail"]

    # Login missing field
    resp5 = client.post("/users/login", json={
        "email": "testuser@example.com"
    })
    assert resp5.status_code == 422
