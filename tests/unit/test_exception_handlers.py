from unittest.mock import MagicMock

import pytest

from app.core.exception_handlers import app_exception_handler
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
    body_bytes = bytes(response.body)
    assert expected_detail in body_bytes.decode()
