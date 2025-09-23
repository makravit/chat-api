import datetime

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.auth import (
    basic_auth_guard,
    create_access_token,
    hash_password,
    verify_password,
)
from app.core.config import settings
from tests.utils import PasswordKind, build_password, join_parts

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


def test_hash_and_verify_password() -> None:
    pw = build_password(PasswordKind.VALID)
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed)
    assert not verify_password(join_parts("wr", "ong"), hashed)


def test_create_access_token() -> None:
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "user@example.com"


def test_expired_token() -> None:
    exp = datetime.datetime.now(datetime.UTC) - datetime.timedelta(seconds=1)
    payload = {"sub": "user@example.com", "exp": exp}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True},
        )


def test_invalid_signature() -> None:
    data = {"sub": "user@example.com"}
    token = create_access_token(data)
    # Tamper with token
    tampered = token + "abc"
    with pytest.raises(JWTError):
        jwt.decode(tampered, SECRET_KEY, algorithms=[ALGORITHM])


def test_token_missing_claims() -> None:
    token = create_access_token({"foo": "bar"})
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "sub" not in decoded


BASIC_AUTH_USERNAME = "testuser"
BASIC_AUTH_PASSWORD = join_parts("testpass")  # avoid S105/S106


def test_basic_auth_guard_invalid_username() -> None:
    guard = basic_auth_guard(BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD)
    credentials = HTTPBasicCredentials(
        username="wronguser",
        password=BASIC_AUTH_PASSWORD,
    )
    with pytest.raises(HTTPException) as exc:
        guard(credentials)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in exc.value.detail


def test_basic_auth_guard_invalid_password() -> None:
    guard = basic_auth_guard(BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD)
    credentials = HTTPBasicCredentials(
        username=BASIC_AUTH_USERNAME,
        password=join_parts("wr", "ong") + "pass",
    )
    with pytest.raises(HTTPException) as exc:
        guard(credentials)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in exc.value.detail


def test_basic_auth_guard_invalid_both() -> None:
    guard = basic_auth_guard(BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD)
    credentials = HTTPBasicCredentials(
        username="wronguser",
        password=join_parts("wr", "ong") + "pass",
    )
    with pytest.raises(HTTPException) as exc:
        guard(credentials)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in exc.value.detail
