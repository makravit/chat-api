
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.core.auth import hash_password
from app.schemas.user import UserRegister, UserLogin
from app.services.user_service import register_user, authenticate_user


def test_register_user_success():
    user = UserRegister(name="Test", email="test@example.com", password="Password1!")
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = None
    repo_mock.create.return_value = SimpleNamespace(id=1, name=user.name, email=user.email)
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        result = register_user(user, MagicMock())
    assert result.email == user.email


def test_register_user_duplicate():
    user = UserRegister(name="Test", email="test@example.com", password="Password1!")
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = MagicMock()
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        with pytest.raises(HTTPException) as exc:
            register_user(user, MagicMock())
    assert exc.value.status_code == 400
    assert "already registered" in exc.value.detail


def test_authenticate_user_success():
    login = UserLogin(email="test@example.com", password="Password1!")
    db_user = MagicMock(email=login.email, hashed_password=hash_password("Password1!"))
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = db_user
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        result = authenticate_user(login, MagicMock())
    assert result.access_token


def test_authenticate_user_wrong_password():
    login = UserLogin(email="test@example.com", password="WrongPass1!")
    db_user = MagicMock(email=login.email, hashed_password=hash_password("Password1!"))
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = db_user
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        with pytest.raises(HTTPException) as exc:
            authenticate_user(login, MagicMock())
    assert exc.value.status_code == 401
    assert "incorrect" in exc.value.detail


def test_authenticate_user_not_found():
    login = UserLogin(email="notfound@example.com", password="Password1!")
    repo_mock = MagicMock()
    repo_mock.get_by_email.return_value = None
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        with pytest.raises(HTTPException) as exc:
            authenticate_user(login, MagicMock())
    assert exc.value.status_code == 401

