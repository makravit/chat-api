from fastapi import status

import pytest

@pytest.fixture
def user_data():
    return {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "Password1!"
    }

@pytest.fixture
def registered_user(client, user_data):
    client.post("/users/register", json=user_data)
    return user_data

def test_register_valid(client):
    resp = client.post("/users/register", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "Password1!"
    })
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    assert data["email"] == "testuser@example.com"

def test_login_valid(client):
    user = {
        "name": "Test User",
        "email": "testlogin@example.com",
        "password": "Password1!"
    }
    client.post("/users/register", json=user)
    resp = client.post("/users/login", json={
        "email": user["email"],
        "password": user["password"]
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_wrong_password(client):
    user = {
        "name": "Test User",
        "email": "testwrongpass@example.com",
        "password": "Password1!"
    }
    client.post("/users/register", json=user)
    resp = client.post("/users/login", json={
        "email": user["email"],
        "password": "WrongPass1!"
    })
    assert resp.status_code == 401
    assert "incorrect" in resp.json()["detail"]


@pytest.mark.parametrize("payload,expected_error", [
    ({"name": " ", "email": "emptyname@example.com", "password": "Password1!"}, "empty"),
    ({"name": "Short Pass", "email": "shortpass@example.com", "password": "Short1!"}, "at least 8"),
    ({"email": "no_name@example.com", "password": "Password1!"}, None),
    ({"name": "No Email", "password": "Password1!"}, None),
    ({"name": "No Password", "email": "nopassword@example.com"}, None),
])
def test_register_invalid_cases(client, payload, expected_error):
    resp = client.post("/users/register", json=payload)
    assert resp.status_code == 422
    if expected_error:
        assert any(expected_error in err["msg"].lower() for err in resp.json().get("detail", []))

def test_register_invalid_email(client):
    resp = client.post("/users/register", json={
        "name": "Invalid Email",
        "email": "not-an-email",
        "password": "Password1!"
    })
    assert resp.status_code == 422
    assert any("email" in err["msg"].lower() for err in resp.json()["detail"])


def test_register_duplicate_email(client):
    # Register first user
    resp = client.post("/users/register", json={
        "name": "DupEmail",
        "email": "dupemail@example.com",
        "password": "Password1!"
    })
    assert resp.status_code == 201
    # Register with same email, different name
    resp2 = client.post("/users/register", json={
        "name": "DupEmail2",
        "email": "dupemail@example.com",
        "password": "Password1!"
    })
    assert resp2.status_code == 409
    assert "already registered" in resp2.json()["detail"].lower()

def test_register_duplicate_username(client):
    # Register first user
    resp = client.post("/users/register", json={
        "name": "DupUser",
        "email": "dupuser1@example.com",
        "password": "Password1!"
    })
    assert resp.status_code == 201
    # Register with same name but different email (should succeed, as only email is unique)
    resp2 = client.post("/users/register", json={
        "name": "DupUser",
        "email": "dupuser2@example.com",
        "password": "Password1!"
    })
    assert resp2.status_code == 201

def test_login_missing_fields(client):
    # Missing email
    resp = client.post("/users/login", json={
        "password": "Password1!"
    })
    assert resp.status_code == 422
    # Missing password
    resp = client.post("/users/login", json={
        "email": "testuser@example.com"
    })
    assert resp.status_code == 422

def test_login_invalid_email_format(client):
    resp = client.post("/users/login", json={
        "email": "not-an-email",
        "password": "Password1!"
    })
    assert resp.status_code == 422

def test_login_unregistered_email(client):
    resp = client.post("/users/login", json={
        "email": "doesnotexist@example.com",
        "password": "Password1!"
    })
    assert resp.status_code == 401
    assert "incorrect" in resp.json().get("detail", "").lower()

def test_register_password_complexity(client):
    resp = client.post("/users/register", json={
        "name": "NoComplex",
        "email": "nocomplex@example.com",
        "password": "password123"
    })
    assert resp.status_code == 422
    assert any("must contain" in err["msg"].lower() for err in resp.json()["detail"])

def test_login_empty_password(client):
    resp = client.post("/users/login", json={
        "email": "testuser@example.com",
        "password": ""
    })
    assert resp.status_code == 422
    assert any("empty" in err["msg"].lower() for err in resp.json()["detail"])
