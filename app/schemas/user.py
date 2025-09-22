"""User-related request and response schemas."""

import re

from pydantic import BaseModel, EmailStr, field_validator


def validate_password_complexity(v: str) -> str:
    """Ensure the password meets length and complexity requirements."""
    if len(v.strip()) < 1:
        msg = "Password cannot be empty."
        raise ValueError(msg)
    if len(v) < 8:
        msg = "Password must be at least 8 characters long."
        raise ValueError(msg)
    if (
        not re.search(r"[A-Za-z]", v)
        or not re.search(r"\d", v)
        or not re.search(r"[!@#$%^&*]", v)
    ):
        msg = (
            "Password must contain letters, numbers, and at least one symbol (!@#$%^&*)"
        )
        raise ValueError(msg)
    return v


class UserRegister(BaseModel):
    """Schema for user registration input."""

    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls: type["UserRegister"], v: str) -> str:
        """Ensure the name is not empty or whitespace only."""
        v = v.strip()
        if len(v) < 1:
            msg = "Name must not be empty."
            raise ValueError(msg)
        return v

    @field_validator("password")
    @classmethod
    def password_complexity(cls: type["UserRegister"], v: str) -> str:
        """Validate the password against complexity policy for registration."""
        return validate_password_complexity(v)


class UserLogin(BaseModel):
    """Schema for user login input."""

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_complexity(cls: type["UserLogin"], v: str) -> str:
        """Validate the password against complexity policy for login."""
        return validate_password_complexity(v)


class UserResponse(BaseModel):
    """Schema for user response output."""

    id: int
    name: str
    email: EmailStr


class TokenResponse(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str = "bearer"
