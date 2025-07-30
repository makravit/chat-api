

import os
import datetime

import pytest
from jose import jwt, ExpiredSignatureError

from app.core.auth import create_access_token, hash_password, verify_password

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

def test_expired_token():
    exp = datetime.datetime.utcnow() - datetime.timedelta(seconds=1)
    payload = {"sub": "user@example.com", "exp": exp}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": True})

def test_invalid_signature():
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    # Tamper with token
    tampered = token + "abc"
    with pytest.raises(Exception):
        jwt.decode(tampered, SECRET_KEY, algorithms=[ALGORITHM])

def test_token_missing_claims():
    token = create_access_token({"foo": "bar"})
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "sub" not in decoded
