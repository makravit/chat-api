

# Standard library imports
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest

# Local application imports
from app.services.user_service import EmailAlreadyRegistered, InvalidCredentials
from app.core.auth import hash_password
from app.services.user_service import register_user, authenticate_user

def test_register_user_success():
    name = "Test"
    email = "test@example.com"
    password = "Password1!"
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = None
    repo_mock.create.return_value = SimpleNamespace(id=1, name=name, email=email)
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        result = register_user(name, email, password, MagicMock())
    assert result.email == email

def test_register_user_duplicate():
    name = "Test"
    email = "test@example.com"
    password = "Password1!"
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = MagicMock()
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        with pytest.raises(EmailAlreadyRegistered):
            register_user(name, email, password, MagicMock())

def test_authenticate_user_success():
    email = "test@example.com"
    password = "Password1!"
    db_user = MagicMock(email=email, hashed_password=hash_password(password))
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = db_user
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        result = authenticate_user(email, password, MagicMock())
    assert isinstance(result, str) and result

def test_authenticate_user_wrong_password():
    email = "test@example.com"
    password = "WrongPass1!"
    db_user = MagicMock(email=email, hashed_password=hash_password("Password1!"))
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = db_user
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        with pytest.raises(InvalidCredentials):
            authenticate_user(email, password, MagicMock())

def test_authenticate_user_not_found():
    email = "notfound@example.com"
    password = "Password1!"
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = None
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        with pytest.raises(InvalidCredentials):
            authenticate_user(email, password, MagicMock())

