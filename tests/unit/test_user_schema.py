import pytest
from pydantic import ValidationError
from app.schemas.user import UserRegister, UserLogin

def test_user_register_valid() -> None:
    """Test that a valid user registration passes schema validation."""
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
def test_user_register_invalid_cases(kwargs: dict, expected_error: str) -> None:
    """Test invalid user registration cases for missing/invalid fields."""
    with pytest.raises(ValidationError) as exc:
        UserRegister(**kwargs)
    if expected_error:
        # Exception messages should be user-friendly and contain the expected error
        assert expected_error in str(exc.value).lower() or expected_error in str(exc).lower()

def test_user_login_valid() -> None:
    """Test that a valid user login passes schema validation."""
    login = UserLogin(email="valid@example.com", password="Password1!")
    assert login.email == "valid@example.com"



@pytest.mark.parametrize("kwargs", [
    dict(password="Password1!"),
    dict(email="valid@example.com"),
])
def test_user_login_missing_fields(kwargs: dict) -> None:
    """Test that missing required login fields raise a validation error."""
    with pytest.raises(ValidationError):
        UserLogin(**kwargs)

def test_user_login_invalid_email() -> None:
    """Test that an invalid email format in login raises a validation error."""
    with pytest.raises(ValidationError):
        UserLogin(email="not-an-email", password="Password1!")


# Additional tests for registration and login edge cases
@pytest.mark.parametrize("kwargs", [
    # Extra/unexpected field
    dict(name="Extra Field", email="extra@example.com", password="Password1!", extra="field"),
    # Whitespace-only name
    dict(name="   ", email="white@example.com", password="Password1!"),
    # Whitespace-only email
    dict(name="White Email", email="   ", password="Password1!"),
    # Password valid length but missing complexity (if complexity is enforced)
    dict(name="NoComplexity", email="nocomp@example.com", password="passwordpassword"),
    # Name at max length (assuming 255)
    dict(name="a"*255, email="maxlen@example.com", password="Password1!"),
    # Email at max length (assuming 255)
    dict(name="Max Email", email=("a"*247)+"@e.com", password="Password1!"),
])
def test_user_register_edge_cases(kwargs: dict) -> None:
    """Test edge cases for user registration schema, including whitespace, max length, and complexity."""
    password = kwargs.get("password", "")
    required_symbols = set("!@#$%^&*")
    has_symbol = bool(set(password) & required_symbols)
    should_error = (
        kwargs.get("name", "").strip() == "" or
        kwargs.get("email", "").strip() == "" or
        ("password" in kwargs and not has_symbol) or
        ("email" in kwargs and len(kwargs["email"].split("@", 1)[0]) > 64)
    )
    try:
        user = UserRegister(**kwargs)
        if should_error:
            assert False, "ValidationError expected for invalid input"
    except ValidationError as exc:
        if not should_error:
            assert False, "Unexpected ValidationError for valid input"
        # Check for the new error message if whitespace-only name or password
        if kwargs.get("name", "").strip() == "" or ("password" in kwargs and kwargs["password"].strip() == ""):
            # Both error messages are user-friendly and consistent
            assert ("Password cannot be empty" in str(exc) or "Name must not be empty." in str(exc))


@pytest.mark.parametrize("kwargs", [
    # Extra/unexpected field
    dict(email="extra@example.com", password="Password1!", extra="field"),
    # Whitespace-only email
    dict(email="   ", password="Password1!"),
    # Whitespace-only password
    dict(email="white@example.com", password="   "),
    # Password valid length but missing complexity (if complexity is enforced)
    dict(email="nocomp@example.com", password="passwordpassword"),
    # Email at max length (assuming 255)
    dict(email=("a"*247)+"@e.com", password="Password1!"),
])
def test_user_login_edge_cases(kwargs: dict) -> None:
    """Test edge cases for user login schema, including whitespace, max length, and complexity."""
    password = kwargs.get("password", "")
    required_symbols = set("!@#$%^&*")
    has_symbol = bool(set(password) & required_symbols)
    should_error = (
        kwargs.get("email", "").strip() == "" or
        ("password" in kwargs and (not has_symbol or kwargs["password"].strip() == "")) or
        ("email" in kwargs and len(kwargs["email"].split("@", 1)[0]) > 64)
    )
    try:
        login = UserLogin(**kwargs)
        if should_error:
            assert False, "ValidationError expected for invalid input"
    except ValidationError as exc:
        if not should_error:
            assert False, "Unexpected ValidationError for valid input"
        # Check for the new error message if whitespace-only password
        if "password" in kwargs and kwargs["password"].strip() == "":
            # Both error messages are user-friendly and consistent
            assert ("Password cannot be empty" in str(exc) or "Password cannot be empty or whitespace only." in str(exc))
