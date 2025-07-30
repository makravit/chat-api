from pydantic import BaseModel, constr, validator


class ChatRequest(BaseModel):
    message: str

    @validator('message')
    def not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Message must not be empty or whitespace.")
        if len(v) > 4096:
            raise ValueError("Message too long. Maximum allowed is 4096 characters. Please shorten your message.")
        return v

class ChatResponse(BaseModel):
    response: str
