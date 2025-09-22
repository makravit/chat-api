import time
from datetime import UTC, datetime

import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from jose import JWTError, jwt

from app.core.auth import (
    ALGORITHM,
    SECRET_KEY,
    basic_auth_guard,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from app.core.config import settings
from tests.utils import join_parts, make_db_query_first, make_dummy_db


def test_create_access_token_extra_keys() -> None:
    data = {"sub": "extra@example.com", "foo": "bar"}
    token = create_access_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "extra@example.com"
    assert payload["foo"] == "bar"
    assert "exp" in payload


def test_create_access_token_minimal() -> None:
    token = create_access_token({"sub": "test@example.com"})
    assert isinstance(token, str)


def test_create_access_token_no_sub() -> None:
    token = create_access_token({})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload
    assert payload.get("sub") is None


def test_create_access_token_empty_dict() -> None:
    token = create_access_token({})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload


def test_get_current_user_invalid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    def bad_decode(
        _token: str,
        _key: str,
        **_kwargs: object,
    ) -> None:
        raise JWTError

    monkeypatch.setattr("app.core.auth.jwt.decode", bad_decode)
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=join_parts("bad-token"), db=make_dummy_db())
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication required" in exc.value.detail


def test_get_current_user_missing_sub(monkeypatch: pytest.MonkeyPatch) -> None:
    def decode(_token: str, _key: str, **_kwargs: object) -> dict:
        return {}

    monkeypatch.setattr("app.core.auth.jwt.decode", decode)
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=join_parts("tok"), db=make_dummy_db())
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication required" in exc.value.detail


def test_get_current_user_user_none(monkeypatch: pytest.MonkeyPatch) -> None:
    def decode(_token: str, _key: str, **_kwargs: object) -> dict:
        return {"sub": "foo@example.com"}

    monkeypatch.setattr("app.core.auth.jwt.decode", decode)
    db = make_db_query_first(None)
    with pytest.raises(HTTPException) as exc:
        get_current_user(token=join_parts("tok"), db=db)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication required" in exc.value.detail


def test_create_access_token_decodes_and_has_exp() -> None:
    data = {"sub": "foo@example.com"}
    token = create_access_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "foo@example.com"
    assert "exp" in payload
    # Expiry should be in the future
    assert payload["exp"] > time.time()


def test_create_access_token_copy_update_logic() -> None:
    data = {"sub": "cover@example.com", "foo": "bar", "baz": 123}
    token = create_access_token(data)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "cover@example.com"
    assert payload["foo"] == "bar"
    assert payload["baz"] == 123
    assert "exp" in payload


def test_create_refresh_token_properties() -> None:
    token, expire = create_refresh_token()
    # basic shape
    assert isinstance(token, str)
    # token_urlsafe(64) yields a fairly long base64url string
    assert len(token) >= 20
    # expiry should be timezone-aware and roughly REFRESH_TOKEN_EXPIRE_DAYS from now
    assert expire.tzinfo is not None
    now = datetime.now(UTC)
    delta_seconds = (expire - now).total_seconds()
    days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    # Use a generous window to avoid flakiness on slow CI
    assert (days - 1) * 86400 <= delta_seconds <= (days + 1) * 86400


def test_basic_auth_guard_success() -> None:
    guard = basic_auth_guard("user", join_parts("pass"))
    creds = HTTPBasicCredentials(username="user", password=join_parts("pass"))
    # Should not raise
    guard(creds)


def test_basic_auth_guard_fail_username() -> None:
    guard = basic_auth_guard("user", join_parts("pass"))
    creds = HTTPBasicCredentials(username="wrong", password=join_parts("pass"))
    with pytest.raises(HTTPException) as exc:
        guard(creds)
    assert exc.value.status_code == 401
    assert "Invalid credentials" in exc.value.detail


def test_basic_auth_guard_fail_password() -> None:
    guard = basic_auth_guard("user", join_parts("pass"))
    creds = HTTPBasicCredentials(username="user", password=join_parts("wr", "ong"))
    with pytest.raises(HTTPException) as exc:
        guard(creds)
    assert exc.value.status_code == 401
    assert "Invalid credentials" in exc.value.detail
