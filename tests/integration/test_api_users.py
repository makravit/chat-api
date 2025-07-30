from fastapi import status

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
    # Register first
    client.post("/users/register", json={
        "name": "Test User",
        "email": "testlogin@example.com",
        "password": "Password1!"
    })
    # Login
    resp = client.post("/users/login", json={
        "email": "testlogin@example.com",
        "password": "Password1!"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_login_wrong_password(client):
    # Register first
    client.post("/users/register", json={
        "name": "Test User",
        "email": "testwrongpass@example.com",
        "password": "Password1!"
    })
    # Login with wrong password
    resp = client.post("/users/login", json={
        "email": "testwrongpass@example.com",
        "password": "WrongPass1!"
    })
    assert resp.status_code == 401
    assert "incorrect" in resp.json()["detail"]

def test_register_empty_name(client):
    resp = client.post("/users/register", json={
        "name": " ",
        "email": "emptyname@example.com",
        "password": "Password1!"
    })
    assert resp.status_code == 422
    assert any("empty" in err["msg"].lower() for err in resp.json()["detail"])

def test_register_short_password(client):
    resp = client.post("/users/register", json={
        "name": "Short Pass",
        "email": "shortpass@example.com",
        "password": "Short1!"
    })
    assert resp.status_code == 422
    assert any("at least 8" in err["msg"].lower() for err in resp.json()["detail"])

def test_register_missing_email(client):
    resp = client.post("/users/register", json={
        "name": "No Email",
        "password": "Password1!"
    })
    assert resp.status_code == 422

def test_register_missing_password(client):
    resp = client.post("/users/register", json={
        "name": "No Password",
        "email": "nopassword@example.com"
    })
    assert resp.status_code == 422

def test_register_missing_name(client):
    resp = client.post("/users/register", json={
        "email": "noname@example.com",
        "password": "Password1!"
    })
    assert resp.status_code == 422

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
    assert resp2.status_code in (400, 409)

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
    assert resp.status_code == 401 or resp.status_code == 400
    assert "not found" in resp.json().get("detail", "").lower() or "incorrect" in resp.json().get("detail", "").lower()

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
