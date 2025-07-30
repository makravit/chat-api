# In-memory user model for demonstration
from typing import Optional
from pydantic import EmailStr

class User:
    def __init__(self, id: int, name: str, email: EmailStr, hashed_password: str):
        self.id = id
        self.name = name
        self.email = email
        self.hashed_password = hashed_password
