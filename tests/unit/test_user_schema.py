


# Third-party imports
import pytest

# Local application imports
from app.schemas.user import validate_password_complexity, UserRegister, UserLogin

def test_validate_password_complexity_valid():
    assert validate_password_complexity("Password1!") == "Password1!"

def test_validate_password_complexity_empty():
    with pytest.raises(ValueError) as exc:
        validate_password_complexity("")
    assert "Password cannot be empty" in str(exc.value)

def test_validate_password_complexity_too_short():
    with pytest.raises(ValueError) as exc:
        validate_password_complexity("Ab1!")
    assert "at least 8 characters" in str(exc.value)

def test_validate_password_complexity_missing_symbol():
    with pytest.raises(ValueError) as exc:
        validate_password_complexity("Password1")
    assert "must contain letters, numbers, and at least one symbol" in str(exc.value)

def test_validate_password_complexity_missing_number():
    with pytest.raises(ValueError) as exc:
        validate_password_complexity("Password!")
    assert "must contain letters, numbers, and at least one symbol" in str(exc.value)

def test_validate_password_complexity_missing_letter():
    with pytest.raises(ValueError) as exc:
        validate_password_complexity("12345678!")
    assert "must contain letters, numbers, and at least one symbol" in str(exc.value)

def test_user_login_valid():
    login = UserLogin(email="valid@example.com", password="Password1!")
    assert login.email == "valid@example.com"

def test_user_register_valid():
    user = UserRegister(name="Valid User", email="valid@example.com", password="Password1!")
    assert user.email == "valid@example.com"

