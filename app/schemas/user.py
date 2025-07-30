from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
import re

class UserRegister(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    email: EmailStr
    password: constr(min_length=8)

    @validator('password')
    def password_complexity(cls, v):
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v) or not re.search(r"[!@#$%^&*]", v):
            raise ValueError("Password must contain letters, numbers, and at least one symbol (!@#$%^&*)")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=1)

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
