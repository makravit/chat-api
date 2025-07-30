
import re
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v):
        v = v.strip()
        if len(v) < 1:
            raise ValueError("Name must not be empty.")
        return v

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Password cannot be empty or whitespace only.")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v) or not re.search(r"[!@#$%^&*]", v):
            raise ValueError("Password must contain letters, numbers, and at least one symbol (!@#$%^&*)")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_complexity(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Password cannot be empty or whitespace only.")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v) or not re.search(r"[!@#$%^&*]", v):
            raise ValueError("Password must contain letters, numbers, and at least one symbol (!@#$%^&*)")
        return v

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
