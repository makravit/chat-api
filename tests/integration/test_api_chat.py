from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

import app.api.chat
from app.core.auth import create_access_token
from app.main import app as main_app


def test_chat_happy_path(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, object]],
) -> None:
    token = login_and_get_tokens()["access_token"]
    resp = client.post(
        "/api/v1/chat",
        json={"message": "Hello!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert "response" in resp.json()


def test_chat_non_hello_message(
    client: TestClient,
    login_and_get_tokens: Callable[[], dict[str, object]],
) -> None:
    token = login_and_get_tokens()["access_token"]
    resp = client.post(
        "/api/v1/chat",
        json={"message": "How are you?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["response"].startswith("I'm here to help!")


def test_chat_unauthenticated(client: TestClient) -> None:
    resp = client.post("/api/v1/chat", json={"message": "Hello!"})
    assert resp.status_code == 401
    # FastAPI default message for missing/invalid Bearer token
    assert resp.json()["detail"] == "Not authenticated"


def test_chat_invalid_token(client: TestClient) -> None:
    # Malformed token
    resp = client.post(
        "/api/v1/chat",
        json={"message": "Hello!"},
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert resp.status_code == 401
    assert (
        resp.json()["detail"] == "Authentication required. Please log in or register."
    )


def test_chat_token_missing_sub(client: TestClient) -> None:
    token = create_access_token({"foo": "bar"})  # no 'sub'
    resp = client.post(
        "/api/v1/chat",
        json={"message": "Hello!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
    assert (
        resp.json()["detail"] == "Authentication required. Please log in or register."
    )


def test_chat_token_nonexistent_user(client: TestClient) -> None:
    token = create_access_token({"sub": "ghost@example.com"})
    resp = client.post(
        "/api/v1/chat",
        json={"message": "Hello!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401
    assert (
        resp.json()["detail"] == "Authentication required. Please log in or register."
    )


@pytest.mark.parametrize(
    ("payload", "expected_error"),
    [
        ({"message": "   "}, "empty"),
        ({"message": "a" * 4097}, "too long"),
        ({}, None),
        ({"message": 12345}, None),
    ],
)
def test_chat_invalid_cases(
    client: TestClient,
    payload: dict[str, object],
    expected_error: str | None,
    login_and_get_tokens: Callable[[], dict[str, object]],
) -> None:
    token = login_and_get_tokens()["access_token"]
    resp = client.post(
        "/api/v1/chat",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
    if expected_error:
        assert any(
            expected_error in err["msg"].lower()
            for err in resp.json().get("detail", [])
        )


def test_chat_service_exception(
    monkeypatch: pytest.MonkeyPatch,
    login_and_get_tokens: Callable[[], dict[str, object]],
) -> None:
    token = login_and_get_tokens()["access_token"]

    class SimulatedServiceError(Exception):
        """Test-only exception to simulate a service failure."""

    def raise_exception(*_args: object, **_kwargs: object) -> None:
        msg = "Simulated service failure"
        raise SimulatedServiceError(msg)

    monkeypatch.setattr(app.api.chat, "process_chat", raise_exception)
    # Use a local client for the full app that returns 500 responses instead of raising
    with TestClient(main_app, raise_server_exceptions=False) as local_client:
        resp = local_client.post(
            "/api/v1/chat",
            json={"message": "Hello!"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 500
