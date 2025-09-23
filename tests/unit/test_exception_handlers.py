from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.core.exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.core.exceptions import (
    AppError,
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exc", "expected_status", "expected_detail"),
    [
        (EmailAlreadyRegisteredError("Email exists!"), 409, "Email exists!"),
        (InvalidCredentialsError("Bad creds!"), 401, "Bad creds!"),
        (AppError("Generic error!"), 500, "Generic error!"),
        (Exception("Unexpected!"), 500, "Unexpected!"),
    ],
)
async def test_app_exception_handler(
    exc: Exception,
    expected_status: int,
    expected_detail: str,
) -> None:
    req = MagicMock()
    response = await app_exception_handler(req, exc)
    assert response.status_code == expected_status
    assert response.body
    body = bytes(response.body).decode()
    assert expected_detail in body
    # All errors include a machine-readable code
    assert '"code"' in body


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
