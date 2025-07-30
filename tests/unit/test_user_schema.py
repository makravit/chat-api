import pytest
from pydantic import ValidationError
from app.schemas.user import UserRegister, UserLogin

def test_user_register_valid():
    user = UserRegister(name="Valid User", email="valid@example.com", password="Password1!")
    assert user.email == "valid@example.com"


import pytest

@pytest.mark.parametrize("kwargs,expected_error", [
    (dict(email="missingname@example.com", password="Password1!"), None),
    (dict(name="No Email", password="Password1!"), None),
    (dict(name="No Password", email="nopassword@example.com"), None),
    (dict(name="Invalid Email", email="not-an-email", password="Password1!"), "email"),
    (dict(name="ShortPW", email="shortpw@example.com", password="123"), "at least 8"),
])
def test_user_register_invalid_cases(kwargs, expected_error):
    with pytest.raises(ValidationError) as exc:
        UserRegister(**kwargs)
    if expected_error:
        assert expected_error in str(exc.value).lower()

def test_user_login_valid():
    login = UserLogin(email="valid@example.com", password="Password1!")
    assert login.email == "valid@example.com"



@pytest.mark.parametrize("kwargs", [
    dict(password="Password1!"),
    dict(email="valid@example.com"),
])
def test_user_login_missing_fields(kwargs):
    with pytest.raises(ValidationError):
        UserLogin(**kwargs)

def test_user_login_invalid_email():
    with pytest.raises(ValidationError):
        UserLogin(email="not-an-email", password="Password1!")
