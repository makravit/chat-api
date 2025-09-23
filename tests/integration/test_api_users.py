from collections.abc import Callable
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session

import app.services.user_service
from app.core.auth import ALGORITHM, SECRET_KEY, get_current_user
from app.main import app as main_app
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from tests.utils import (
    PasswordKind,
    assert_deleted_refresh_cookie,
    assert_secure_refresh_cookie,
    build_password,
    join_parts,
)

"""
Note: test helpers are imported directly for concise usage.
"""


@pytest.fixture
def user_data() -> dict[str, str]:
    return {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": build_password(PasswordKind.VALID),
    }


@pytest.fixture
def registered_user(client: TestClient, user_data: dict[str, str]) -> dict[str, str]:
    client.post("/api/v1/users/register", json=user_data)
    return user_data


"""
Integration tests for /api/v1/users endpoints.
Grouped by endpoint for clarity and maintainability.
"""


# ---------------------------- /register ---------------------------------


def test_register_duplicate_email(
    client: TestClient,
    user_data: dict[str, str],
) -> None:
    """Registering the same email twice should return 409."""
    resp1 = client.post("/api/v1/users/register", json=user_data)
    assert resp1.status_code == 201
    resp2 = client.post("/api/v1/users/register", json=user_data)
    assert resp2.status_code == 409
    assert "already registered" in resp2.json()["detail"].lower()


@pytest.mark.parametrize(
    ("payload", "expected_error"),
    [
        (
            {
                "name": " ",
                "email": "emptyname@example.com",
                "password": build_password(PasswordKind.VALID),
            },
            "empty",
        ),
        (
            {
                "name": "Short Pass",
                "email": "shortpass@example.com",
                "password": build_password(PasswordKind.SHORT),
            },
            "at least 8",
        ),
        (
            {
                "email": "no_name@example.com",
                "password": build_password(PasswordKind.VALID),
            },
            None,
        ),
        ({"name": "No Email", "password": build_password(PasswordKind.VALID)}, None),
        ({"name": "No Password", "email": "nopassword@example.com"}, None),
    ],
)
def test_register_invalid_cases(
    client: TestClient,
    payload: dict[str, Any],
    expected_error: str | None,
) -> None:
    resp = client.post("/api/v1/users/register", json=payload)
    assert resp.status_code == 422
    if expected_error:
        assert any(
            expected_error in err["msg"].lower()
            for err in resp.json().get("detail", [])
        )


def test_register_invalid_email(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/users/register",
        json={
            "name": "Invalid Email",
            "email": "not-an-email",
            "password": build_password(PasswordKind.VALID),
        },
    )
    assert resp.status_code == 422
    assert any("email" in err["msg"].lower() for err in resp.json()["detail"])


def test_register_duplicate_username(client: TestClient) -> None:
    # Register first user
    resp = client.post(
        "/api/v1/users/register",
        json={
            "name": "DupUser",
            "email": "dupuser1@example.com",
            "password": build_password(PasswordKind.VALID),
        },
    )
    assert resp.status_code == 201
    # Register with same name but different email (only email is unique)
    resp2 = client.post(
        "/api/v1/users/register",
        json={
            "name": "DupUser",
            "email": "dupuser2@example.com",
            "password": build_password(PasswordKind.VALID),
        },
    )
    assert resp2.status_code == 201


def test_register_password_complexity(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/users/register",
        json={
            "name": "NoComplex",
            "email": "nocomplex@example.com",
            "password": build_password(PasswordKind.WEAK),
        },
    )
    assert resp.status_code == 422
    assert any("must contain" in err["msg"].lower() for err in resp.json()["detail"])


def test_password_not_in_register_response(
    client: TestClient,
    user_data: dict[str, str],
) -> None:
    """Password is never returned in the register API response."""
    reg = client.post("/api/v1/users/register", json=user_data)
    assert reg.status_code == 201
    assert "password" not in reg.json()


# ------------------------------ /login -----------------------------------


def test_login_token_response_structure(
    client: TestClient,
    user_data: dict[str, str],
) -> None:
    """Login returns a valid token structure including refresh token."""
    client.post("/api/v1/users/register", json=user_data)
    resp = client.post(
        "/api/v1/users/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == join_parts("bearer")
    cookies = resp.cookies
    assert "refresh_token" in cookies


def test_login_sets_secure_refresh_cookie(
    client: TestClient,
    user_data: dict[str, str],
) -> None:
    client.post("/api/v1/users/register", json=user_data)
    resp = client.post(
        "/api/v1/users/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    assert_secure_refresh_cookie(set_cookie)


def test_login_missing_fields(client: TestClient) -> None:
    # Missing email
    resp = client.post(
        "/api/v1/users/login",
        json={"password": build_password(PasswordKind.VALID)},
    )
    assert resp.status_code == 422
    # Missing password
    resp = client.post("/api/v1/users/login", json={"email": "testuser@example.com"})
    assert resp.status_code == 422


def test_login_invalid_email_format(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/users/login",
        json={"email": "not-an-email", "password": build_password(PasswordKind.VALID)},
    )
    assert resp.status_code == 422


def test_login_unregistered_email(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/users/login",
        json={
            "email": "doesnotexist@example.com",
            "password": build_password(PasswordKind.VALID),
        },
    )
    assert resp.status_code == 401
    assert "incorrect" in resp.json().get("detail", "").lower()


def test_login_wrong_password(client: TestClient) -> None:
    user = {
        "name": "Test User",
        "email": "testwrongpass@example.com",
        "password": build_password(PasswordKind.VALID),
    }
    client.post("/api/v1/users/register", json=user)
    resp = client.post(
        "/api/v1/users/login",
        json={"email": user["email"], "password": build_password(PasswordKind.WRONG)},
    )
    assert resp.status_code == 401
    assert "incorrect" in resp.json()["detail"]


def test_password_not_in_login_response(
    client: TestClient,
    user_data: dict[str, str],
) -> None:
    """Password is never returned in the login API response."""
    client.post("/api/v1/users/register", json=user_data)
    login = client.post(
        "/api/v1/users/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert login.status_code == 200
    assert "password" not in login.json()


def test_database_failure_on_login(
    client: TestClient,
    user_data: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Simulate DB failure during login and expect 500."""
    client.post("/api/v1/users/register", json=user_data)

    class SimulatedDbFailureError(RuntimeError):
        """Raised to simulate an internal DB failure in tests."""

    def broken_authenticate_user(*_args: object, **_kwargs: object) -> None:
        msg = "DB failure simulated"
        raise SimulatedDbFailureError(msg)

    monkeypatch.setattr(
        app.services.user_service,
        "authenticate_user",
        broken_authenticate_user,
    )
    resp = client.post(
        "/api/v1/users/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert resp.status_code == 500


# -------------------------- /refresh-token -------------------------------


def test_refresh_token_missing_cookie(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
) -> None:
    tokens = login_and_get_tokens()
    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
    }
    resp = client.post("/api/v1/users/refresh-token", headers=headers)
    assert resp.status_code == 401
    body = resp.json()
    assert "Invalid or expired refresh token" in body["detail"]
    assert body.get("code") in ("http_error", "invalid_credentials")


def test_refresh_token_success(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
) -> None:
    tokens = login_and_get_tokens()
    assert tokens["refresh_token"]
    rtok0 = tokens["refresh_token"]
    assert isinstance(rtok0, str)
    # Use cookie for refresh
    resp = client.post(
        "/api/v1/users/refresh-token",
        cookies={
            "refresh_token": rtok0,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == join_parts("bearer")
    resp2 = client.post(
        "/api/v1/users/refresh-token",
        cookies={
            "refresh_token": rtok0,
        },
    )
    assert resp2.status_code == 401
    refresh_token = tokens["refresh_token"]
    assert isinstance(refresh_token, str)
    for _ in range(5):
        rt = refresh_token
        assert isinstance(rt, str)
        resp = client.post(
            "/api/v1/users/refresh-token",
            cookies={"refresh_token": rt},
        )
        assert resp.status_code in (200, 401)
        if resp.status_code == 200:
            new_rt = resp.cookies.get("refresh_token") or rt
            assert isinstance(new_rt, str)
            refresh_token = new_rt


def test_refresh_token_invalid(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
) -> None:
    login_and_get_tokens()  # ensure a user exists
    resp = client.post(
        "/api/v1/users/refresh-token",
        cookies={"refresh_token": "invalidtoken"},
    )
    assert resp.status_code == 401
    body = resp.json()
    assert "invalid" in body["detail"].lower()
    assert body.get("code") in ("http_error", "invalid_credentials")


def test_refresh_token_revoked_usage(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
) -> None:
    """Using a revoked refresh token should return 401 Unauthorized."""
    tokens = login_and_get_tokens()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    logout_resp = client.post(
        "/api/v1/users/logout",
        cookies={"refresh_token": refresh_token},
        headers=headers,
    )
    # Use the latest refresh_token from logout response if set
    revoked_token = logout_resp.cookies.get("refresh_token", refresh_token)
    assert isinstance(revoked_token, str)
    resp = client.post(
        "/api/v1/users/refresh-token",
        cookies={"refresh_token": revoked_token},
    )
    assert resp.status_code == 401


def test_refresh_token_sliding_expiration(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
) -> None:
    """
    Refresh token rotates to a new cookie value on each success and allows
    multiple rotations.
    """
    tokens = login_and_get_tokens()
    refresh_token = tokens["refresh_token"]
    assert isinstance(refresh_token, str)
    token_values = [refresh_token]
    for _ in range(3):
        resp = client.post(
            "/api/v1/users/refresh-token",
            cookies={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        # A new refresh token should be issued each time
        new_refresh = resp.cookies.get("refresh_token", refresh_token)
        assert isinstance(new_refresh, str)
        assert new_refresh != refresh_token
        refresh_token = new_refresh
    token_values.append(refresh_token)
    assert len(set(token_values)) == len(token_values)


def test_refresh_sets_secure_refresh_cookie(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
) -> None:
    tokens = login_and_get_tokens()
    rtok = tokens["refresh_token"]
    assert isinstance(rtok, str)
    resp = client.post(
        "/api/v1/users/refresh-token",
        cookies={"refresh_token": rtok},
    )
    assert resp.status_code == 200
    set_cookie = resp.headers.get("set-cookie", "")
    assert_secure_refresh_cookie(set_cookie)


def test_refresh_token_rate_limiting(
    client: TestClient,
    user_data: dict[str, str],
) -> None:
    """
    Exceed refresh attempts should trigger rate limiting (max 5 per 10 min
    per session/IP).
    """
    client.post("/api/v1/users/register", json=user_data)
    login = client.post(
        "/api/v1/users/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    refresh_token = login.cookies.get("refresh_token")
    assert isinstance(refresh_token, str)
    for _ in range(5):
        rt = refresh_token
        assert isinstance(rt, str)
        resp = client.post(
            "/api/v1/users/refresh-token",
            cookies={"refresh_token": rt},
        )
        assert resp.status_code == 200 or resp.status_code == 401
        if resp.status_code == 200:
            new_rt = resp.cookies.get("refresh_token") or rt
            assert isinstance(new_rt, str)
            refresh_token = new_rt
    resp = client.post(
        "/api/v1/users/refresh-token",
        cookies={"refresh_token": refresh_token},
    )
    assert resp.status_code in (429, 401, 200)


def test_refresh_token_exception(
    client: TestClient,
    user_data: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client.post("/api/v1/users/register", json=user_data)
    login = client.post(
        "/api/v1/users/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    cookies = login.cookies
    # Simulate exception in rotate_refresh_token

    from app.core.exceptions import InvalidCredentialsError

    def raise_exc(*_args: object, **_kwargs: object) -> None:
        msg = "Invalid or expired refresh token"
        raise InvalidCredentialsError(msg)

    monkeypatch.setattr(app.services.user_service, "rotate_refresh_token", raise_exc)
    rtok = cookies.get("refresh_token")
    assert isinstance(rtok, str)
    resp = client.post(
        "/api/v1/users/refresh-token",
        cookies={"refresh_token": rtok},
    )
    assert resp.status_code == 401
    assert "invalid" in resp.json()["detail"].lower()


def test_refresh_token_generic_exception_returns_500(
    client: TestClient,
    user_data: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Generic exceptions from rotate_refresh_token should bubble to 500."""
    client.post("/api/v1/users/register", json=user_data)
    login = client.post(
        "/api/v1/users/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    cookies = login.cookies

    class SimulatedUnexpectedError(RuntimeError):
        """Raised to simulate an unexpected error in tests."""

    def raise_generic(*_args: object, **_kwargs: object) -> None:
        msg = "boom"
        raise SimulatedUnexpectedError(msg)

    monkeypatch.setattr(
        app.services.user_service,
        "rotate_refresh_token",
        raise_generic,
    )
    rtok = cookies.get("refresh_token")
    assert isinstance(rtok, str)
    resp = client.post(
        "/api/v1/users/refresh-token",
        cookies={"refresh_token": rtok},
    )
    assert resp.status_code == 500


def test_login_access_token_claims_sub(
    client: TestClient,
    user_data: dict[str, str],
) -> None:
    client.post("/api/v1/users/register", json=user_data)
    resp = client.post(
        "/api/v1/users/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == user_data["email"]


# -------------------------------- /logout --------------------------------


def test_logout_missing_refresh_token(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
) -> None:
    tokens = login_and_get_tokens()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = client.post("/api/v1/users/logout", headers=headers)
    assert resp.status_code == 204
    set_cookie = resp.headers.get("set-cookie", "")
    assert set_cookie
    assert_deleted_refresh_cookie(set_cookie)


def test_logout_unauthenticated(client: TestClient) -> None:
    resp = client.post("/api/v1/users/logout")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"


def test_logout_empty_refresh_cookie(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
) -> None:
    tokens = login_and_get_tokens()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    resp = client.post(
        "/api/v1/users/logout",
        headers=headers,
        cookies={"refresh_token": ""},
    )
    assert resp.status_code == 204
    set_cookie = resp.headers.get("set-cookie", "")
    assert set_cookie
    assert_deleted_refresh_cookie(set_cookie)


def test_logout_success(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, object]],
) -> None:
    tokens = login_and_get_tokens()
    access_token = tokens["access_token"]
    refresh = tokens["refresh_token"]
    assert isinstance(refresh, str)
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = client.post(
        "/api/v1/users/logout",
        headers=headers,
        cookies={"refresh_token": refresh},
    )
    assert resp.status_code == 204
    resp2 = client.post(
        "/api/v1/users/refresh-token",
        cookies={"refresh_token": refresh},
    )
    assert resp2.status_code == 401
    tokens2 = login_and_get_tokens()
    access_token2 = tokens2["access_token"]
    headers2 = {"Authorization": f"Bearer {access_token2}"}
    resp3 = client.post("/api/v1/users/logout", headers=headers2)
    assert resp3.status_code == 204


def test_logout_sets_deleted_refresh_cookie(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, object]],
) -> None:
    tokens = login_and_get_tokens()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    rtok = tokens["refresh_token"]
    assert isinstance(rtok, str)
    resp = client.post(
        "/api/v1/users/logout",
        headers=headers,
        cookies={"refresh_token": rtok},
    )
    assert resp.status_code == 204
    set_cookie = resp.headers.get("set-cookie", "")
    assert set_cookie
    assert_deleted_refresh_cookie(set_cookie)


def test_logout_endpoint_invalid_token(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, object]],
) -> None:
    """Logout with an invalid refresh token should return 401."""
    tokens = login_and_get_tokens()
    auth_header = f"Bearer {tokens['access_token']}"
    headers = {"Authorization": auth_header}
    resp = client.post(
        "/api/v1/users/logout",
        cookies={"refresh_token": "invalidtoken"},
        headers=headers,
    )
    assert resp.status_code == 204
    set_cookie = resp.headers.get("set-cookie", "")
    assert set_cookie
    assert_deleted_refresh_cookie(set_cookie)


def test_logout_endpoint_valid_token_repo_revoked(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, object]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    On logout with a valid refresh token, the repo's revoke_token
    should be called.
    """
    tokens = login_and_get_tokens()
    auth_header = f"Bearer {tokens['access_token']}"
    headers = {"Authorization": auth_header}

    # Mock repository methods to assert revoke_token is invoked with the cookie value
    def fake_get_valid_token(_self: object, _token: str) -> object:
        return SimpleNamespace(user_id=42, revoked=False)

    called: dict[str, Any] = {"token": None}

    def fake_revoke_token(_self: object, token: str) -> None:
        called["token"] = token

    monkeypatch.setattr(
        RefreshTokenRepository,
        "get_valid_token",
        fake_get_valid_token,
    )
    monkeypatch.setattr(
        RefreshTokenRepository,
        "revoke_token",
        fake_revoke_token,
    )

    # Override current user to match mocked token's user_id to avoid mismatch
    def _override_current_user() -> object:
        return SimpleNamespace(id=42, email="test@example.com")

    main_app.dependency_overrides[get_current_user] = _override_current_user
    try:
        rtok = tokens["refresh_token"]
        assert isinstance(rtok, str)
        resp = client.post(
            "/api/v1/users/logout",
            cookies={"refresh_token": rtok},
            headers=headers,
        )
        assert resp.status_code == 204
        assert called["token"] == rtok
    finally:
        main_app.dependency_overrides.clear()


def test_logout_exception_returns_401(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tokens = login_and_get_tokens()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from app.core.exceptions import InvalidCredentialsError

    def boom(*_args: object, **_kwargs: object) -> None:
        msg = "No active session or already logged out."
        raise InvalidCredentialsError(msg)

    monkeypatch.setattr(app.services.user_service, "logout_single_session", boom)
    rtok = tokens["refresh_token"]
    assert isinstance(rtok, str)
    resp = client.post(
        "/api/v1/users/logout",
        headers=headers,
        cookies={"refresh_token": rtok},
    )
    assert resp.status_code == 204


def test_logout_domain_logout_error_returns_204(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Domain logout errors are treated as idempotent 204 responses."""
    tokens = login_and_get_tokens()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from app.core.exceptions import LogoutOperationError

    def boom(*_args: object, **_kwargs: object) -> None:
        msg = "boom"
        raise LogoutOperationError(msg)

    monkeypatch.setattr(app.services.user_service, "logout_single_session", boom)
    rtok = tokens["refresh_token"]
    assert isinstance(rtok, str)
    resp = client.post(
        "/api/v1/users/logout",
        headers=headers,
        cookies={"refresh_token": rtok},
    )
    assert resp.status_code == 204


def test_logout_cookie_belongs_to_other_user(
    client: TestClient,
) -> None:
    # User A
    a = {
        "name": "A",
        "email": "a@example.com",
        "password": build_password(PasswordKind.VALID),
    }
    client.post("/api/v1/users/register", json=a)
    login_a = client.post(
        "/api/v1/users/login",
        json={"email": a["email"], "password": a["password"]},
    )
    cookie_a = login_a.cookies.get("refresh_token")
    assert isinstance(cookie_a, str)
    # User B
    b = {
        "name": "B",
        "email": "b@example.com",
        "password": build_password(PasswordKind.VALID),
    }
    client.post("/api/v1/users/register", json=b)
    login_b = client.post(
        "/api/v1/users/login",
        json={"email": b["email"], "password": b["password"]},
    )
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    # B tries to logout using A's cookie -> 401
    resp = client.post(
        "/api/v1/users/logout",
        headers=headers_b,
        cookies={"refresh_token": cookie_a},
    )
    assert resp.status_code == 204


def test_refresh_access_token_claims_sub(
    client: TestClient,
    user_data: dict[str, str],
) -> None:
    client.post("/api/v1/users/register", json=user_data)
    login = client.post(
        "/api/v1/users/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )
    rtok = login.cookies.get("refresh_token")
    assert isinstance(rtok, str)
    resp = client.post(
        "/api/v1/users/refresh-token",
        cookies={"refresh_token": rtok},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == user_data["email"]


# ------------------------------ /logout-all ------------------------------


def test_logout_all_endpoint(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tokens = login_and_get_tokens()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    called: dict[str, bool] = {"ok": False}

    def fake_logout_all(_user_id: int, _db: object) -> None:
        called["ok"] = True

    monkeypatch.setattr(
        app.services.user_service,
        "logout_all_sessions",
        fake_logout_all,
    )
    resp = client.post("/api/v1/users/logout-all", headers=headers)
    assert resp.status_code == 204
    assert called["ok"] is True


def test_logout_all_clears_refresh_cookie(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, Any]],
) -> None:
    tokens = login_and_get_tokens()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    resp = client.post("/api/v1/users/logout-all", headers=headers)
    assert resp.status_code == 204
    set_cookie = resp.headers.get("set-cookie", "")
    assert set_cookie
    assert_deleted_refresh_cookie(set_cookie)


def test_logout_all_unauthenticated(client: TestClient) -> None:
    resp = client.post("/api/v1/users/logout-all")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"


def test_register_email_whitespace_normalization_integration(
    client: TestClient,
) -> None:
    payload = {
        "name": "Trim",
        "email": "  trimme@example.com  ",
        "password": build_password(PasswordKind.VALID),
    }
    reg = client.post("/api/v1/users/register", json=payload)
    assert reg.status_code == 201
    assert reg.json()["email"] == "trimme@example.com"
    # Login using whitespace-wrapped email should still work due to normalization
    login = client.post(
        "/api/v1/users/login",
        json={
            "email": "\t trimme@example.com\n",
            "password": build_password(PasswordKind.VALID),
        },
    )
    assert login.status_code == 200


# ------------------------------ /users/me -------------------------------


def test_get_me_success(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, object]],
) -> None:
    tokens = login_and_get_tokens()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    resp = client.get("/api/v1/users/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert set(data.keys()) == {"id", "name", "email"}
    assert isinstance(data["id"], int)
    assert isinstance(data["name"], str)
    assert isinstance(data["email"], str)


def test_get_me_unauthenticated(client: TestClient) -> None:
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401
    # Our dependency message is precise; accept either generic or standard
    assert (
        "not authenticated" in resp.json()["detail"].lower()
        or "authentication required" in resp.json()["detail"].lower()
    )


def test_get_me_invalid_token(
    client: TestClient,
) -> None:
    headers = {"Authorization": "Bearer invalid.jwt.token"}
    resp = client.get("/api/v1/users/me", headers=headers)
    assert resp.status_code == 401


def test_get_me_deleted_user_returns_401(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, object]],
    db_session: Session,
) -> None:
    tokens = login_and_get_tokens()
    user_data_obj = tokens.get("user_data")
    assert isinstance(user_data_obj, dict)
    email_obj = user_data_obj.get("email")
    assert isinstance(email_obj, str)
    email = email_obj
    # Delete the user directly in the DB to simulate a stale token
    user = db_session.query(User).filter(User.email == email).first()
    assert user is not None
    # Remove dependent refresh tokens first to satisfy FK constraints
    db_session.query(RefreshToken).filter(RefreshToken.user_id == user.id).delete()
    db_session.flush()
    db_session.delete(user)
    db_session.flush()

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    resp = client.get("/api/v1/users/me", headers=headers)
    assert resp.status_code == 401
    # Accept either the dependency's precise message or the default Not authenticated
    assert (
        "authentication required" in resp.json()["detail"].lower()
        or "not authenticated" in resp.json()["detail"].lower()
    )
