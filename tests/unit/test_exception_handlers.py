
from app.core.exceptions import AppException, EmailAlreadyRegistered, InvalidCredentials
from app.core.exception_handlers import app_exception_handler

# Standard library imports
from unittest.mock import MagicMock

# Third-party imports
import pytest
pytestmark = pytest.mark.asyncio

@pytest.mark.asyncio
@pytest.mark.parametrize("exc,expected_status,expected_detail", [
    (EmailAlreadyRegistered("Email exists!"), 409, "Email exists!"),
    (InvalidCredentials("Bad creds!"), 401, "Bad creds!"),
    (AppException("Generic error!"), 500, "Generic error!")
])
async def test_app_exception_handler(exc, expected_status, expected_detail):
    req = MagicMock()
    response = await app_exception_handler(req, exc)
    assert response.status_code == expected_status
    assert response.body
    assert expected_detail in response.body.decode()
