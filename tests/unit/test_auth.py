
import os
import pytest
from jose import jwt

from app.core.auth import hash_password, verify_password, create_access_token

SECRET_KEY = os.getenv("SECRET_KEY", "secret-key")
ALGORITHM = "HS256"

def test_hash_and_verify_password():
    pw = "Password1!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)
    assert not verify_password("wrong", hashed)

def test_create_access_token():
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "user@example.com"
