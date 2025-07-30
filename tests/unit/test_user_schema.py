import pytest
from pydantic import ValidationError
from app.schemas.user import UserRegister, UserLogin

def test_user_register_valid():
    user = UserRegister(name="Valid User", email="valid@example.com", password="Password1!")
    assert user.email == "valid@example.com"

def test_user_register_missing_name():
    with pytest.raises(ValidationError):
        UserRegister(email="missingname@example.com", password="Password1!")

def test_user_register_missing_email():
    with pytest.raises(ValidationError):
        UserRegister(name="No Email", password="Password1!")

def test_user_register_missing_password():
    with pytest.raises(ValidationError):
        UserRegister(name="No Password", email="nopassword@example.com")

def test_user_register_invalid_email():
    with pytest.raises(ValidationError):
        UserRegister(name="Invalid Email", email="not-an-email", password="Password1!")

def test_user_register_short_password():
    with pytest.raises(ValidationError):
        UserRegister(name="ShortPW", email="shortpw@example.com", password="123")

def test_user_login_valid():
    login = UserLogin(email="valid@example.com", password="Password1!")
    assert login.email == "valid@example.com"

def test_user_login_missing_email():
    with pytest.raises(ValidationError):
        UserLogin(password="Password1!")

def test_user_login_missing_password():
    with pytest.raises(ValidationError):
        UserLogin(email="valid@example.com")

def test_user_login_invalid_email():
    with pytest.raises(ValidationError):
        UserLogin(email="not-an-email", password="Password1!")
