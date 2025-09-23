from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.exception_handlers import (
    email_already_registered_handler,
    http_exception_handler,
    invalid_credentials_handler,
    logout_no_session_handler,
    logout_operation_error_handler,
    unhandled_exception_handler,
)
from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    LogoutNoSessionError,
    LogoutOperationError,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_email_already_registered_handler_returns_409() -> None:
    req = MagicMock()
    exc = EmailAlreadyRegisteredError("Email exists!")
    response = await email_already_registered_handler(req, exc)
    assert response.status_code == 409
    body = bytes(response.body).decode()
    assert "Email exists!" in body
    assert '"code"' in body


async def test_invalid_credentials_handler_returns_401_and_clears_cookie() -> None:
    req = MagicMock()
    exc = InvalidCredentialsError("Bad creds!")
    response = await invalid_credentials_handler(req, exc)
    assert response.status_code == 401
    body = bytes(response.body).decode()
    assert "Bad creds!" in body
    assert '"code"' in body
    set_cookie = response.headers.get("set-cookie", "").lower()
    assert "refresh_token=" in set_cookie
    assert "max-age=0" in set_cookie


@pytest.mark.asyncio
async def test_http_exception_handler_preserves_status_and_headers() -> None:
    req = MagicMock()
    exc = HTTPException(status_code=418, detail="I'm a teapot", headers={"X-Test": "1"})
    response = await http_exception_handler(req, exc)
    assert response.status_code == 418
    body = bytes(response.body).decode()
    assert "teapot" in body
    assert response.headers.get("X-Test") == "1"
    assert '"code"' in body


@pytest.mark.asyncio
async def test_http_exception_handler_non_http_fallback() -> None:
    req = MagicMock()
    response = await http_exception_handler(req, Exception("boom"))
    assert response.status_code == 500
    body = bytes(response.body).decode()
    assert "Internal server error" in body
    assert '"code"' in body


@pytest.mark.asyncio
async def test_unhandled_exception_handler_returns_500() -> None:
    req = MagicMock()
    response = await unhandled_exception_handler(req, RuntimeError("boom"))
    assert response.status_code == 500
    body = bytes(response.body).decode()
    assert "Internal server error" in body
    assert '"code"' in body


@pytest.mark.asyncio
async def test_http_exception_handler_without_detail_returns_code_only() -> None:
    req = MagicMock()
    exc = HTTPException(
        status_code=401, detail=None, headers={"WWW-Authenticate": "Bearer"}
    )
    response = await http_exception_handler(req, exc)
    assert response.status_code == 401
    body = bytes(response.body).decode()
    assert '"code"' in body
    assert '"detail"' not in body
    assert response.headers.get("WWW-Authenticate") == "Bearer"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "handler_exc",
    [
        (logout_no_session_handler, LogoutNoSessionError("No session")),
        (logout_operation_error_handler, LogoutOperationError("Op fail")),
    ],
)
async def test_logout_variants_return_204_and_clear_cookie(
    handler_exc: tuple[Callable[..., Any], Exception],
) -> None:
    handler, exc = handler_exc
    req = MagicMock()
    response = await handler(req, exc)
    assert response.status_code == 204
    # Starlette's delete_cookie sets a Set-Cookie header with max-age=0
    # on the Response; ensure the refresh cookie is being cleared.
    set_cookie = response.headers.get("set-cookie", "")
    assert "refresh_token=" in set_cookie.lower()
    assert "max-age=0" in set_cookie.lower()


async def test_unhandled_exception_handler_returns_500_for_generic_error() -> None:
    req = MagicMock()
    response = await unhandled_exception_handler(req, Exception("Unexpected!"))
    assert response.status_code == 500
    body = bytes(response.body).decode()
    assert "Internal server error" in body
    assert '"code"' in body
