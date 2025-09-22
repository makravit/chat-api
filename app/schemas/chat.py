"""Schemas for chat request/response payloads."""

from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    """Request body for chat interactions."""

    message: str

    @field_validator("message")
    @classmethod
    def not_empty(cls: type["ChatRequest"], v: str) -> str:
        """Validate that message is non-empty and within size limits."""
        v = v.strip()
        if not v:
            msg = "Message must not be empty or whitespace."
            raise ValueError(msg)
        if len(v) > 4096:
            msg = (
                "Message too long. Maximum allowed is 4096 characters. "
                "Please shorten your message."
            )
            raise ValueError(msg)
        return v


class ChatResponse(BaseModel):
    """Response body containing the bot's reply."""

    response: str
