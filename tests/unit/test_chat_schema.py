import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatRequest


def test_chat_request_valid() -> None:
    req = ChatRequest(message="Hello!")
    assert req.message == "Hello!"


def test_chat_request_empty() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(message="   ")


def test_chat_request_too_long() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(message="a" * 4097)


def test_chat_request_boundary_length_ok() -> None:
    # 4096 should be accepted
    msg = "a" * 4096
    req = ChatRequest(message=msg)
    assert req.message == msg
