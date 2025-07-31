

# Standard library imports
import re
from typing import Optional

# Third-party imports
from pydantic import BaseModel, EmailStr, field_validator


def validate_password_complexity(v: str) -> str:
    """Ensure the password is not empty, meets length and complexity requirements."""
    if len(v.strip()) < 1:
        raise ValueError("Password cannot be empty.")
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v) or not re.search(r"[!@#$%^&*]", v):
        raise ValueError("Password must contain letters, numbers, and at least one symbol (!@#$%^&*)")
    return v


class UserRegister(BaseModel):
    """Schema for user registration input."""
    name: str
    email: EmailStr
    password: str

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure the name is not empty or whitespace only."""
        v = v.strip()
        if len(v) < 1:
            raise ValueError("Name must not be empty.")
        return v

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
        return validate_password_complexity(v)


class UserLogin(BaseModel):
    """Schema for user login input."""
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v: str) -> str:
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
