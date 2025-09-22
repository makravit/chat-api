import pytest

from app.schemas.user import UserLogin, UserRegister, validate_password_complexity
from tests.utils import build_password


def test_validate_password_complexity_valid() -> None:
    pw = build_password("valid")
    assert validate_password_complexity(pw) == pw


def test_validate_password_complexity_empty() -> None:
    with pytest.raises(ValueError, match="cannot be empty") as exc:
        validate_password_complexity("")
    assert "Password cannot be empty" in str(exc.value)


def test_validate_password_complexity_too_short() -> None:
    with pytest.raises(ValueError, match="at least 8") as exc:
        validate_password_complexity("Ab1!")
    assert "at least 8 characters" in str(exc.value)


def test_validate_password_complexity_missing_symbol() -> None:
    with pytest.raises(ValueError, match="must contain") as exc:
        validate_password_complexity(build_password("missing_symbol"))
    assert "must contain letters, numbers, and at least one symbol" in str(exc.value)


def test_validate_password_complexity_missing_number() -> None:
    with pytest.raises(ValueError, match="must contain") as exc:
        validate_password_complexity(build_password("missing_number"))
    assert "must contain letters, numbers, and at least one symbol" in str(exc.value)


def test_validate_password_complexity_missing_letter() -> None:
    with pytest.raises(ValueError, match="must contain") as exc:
        validate_password_complexity("12345678!")
    assert "must contain letters, numbers, and at least one symbol" in str(exc.value)


def test_user_login_valid() -> None:
    login = UserLogin(email="valid@example.com", password=build_password("valid"))
    assert login.email == "valid@example.com"


def test_user_register_valid() -> None:
    user = UserRegister(
        name="Valid User",
        email="valid@example.com",
        password=build_password("valid"),
    )
    assert user.email == "valid@example.com"


def test_user_register_email_surrounded_whitespace_is_normalized() -> None:
    user = UserRegister(
        name="Trim Email",
        email="  trimmed@example.com  ",
        password=build_password("valid"),
    )
    # Assert current behavior: surrounding whitespace is removed by the schema
    assert user.email == "trimmed@example.com"


def test_user_login_email_surrounded_whitespace_is_normalized() -> None:
    login = UserLogin(email="\t user@example.com \n", password=build_password("valid"))
    # Assert current behavior: surrounding whitespace is removed by the schema
    assert login.email == "user@example.com"
