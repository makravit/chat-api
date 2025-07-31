

# Standard library imports

# Third-party imports
from pydantic import BaseModel, field_validator

# Local application imports

class ChatRequest(BaseModel):
    message: str

    @field_validator('message')
    @classmethod
    def not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Message must not be empty or whitespace.")
        if len(v) > 4096:
            raise ValueError("Message too long. Maximum allowed is 4096 characters. Please shorten your message.")
        return v

class ChatResponse(BaseModel):
    response: str
