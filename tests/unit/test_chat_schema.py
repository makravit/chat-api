
# Standard library imports

# Third-party imports
import pytest

# Local application imports
from app.schemas.chat import ChatRequest
from pydantic import ValidationError


def test_chat_request_valid():
    req = ChatRequest(message="Hello!")
    assert req.message == "Hello!"

def test_chat_request_empty():
    with pytest.raises(ValidationError):
        ChatRequest(message="   ")

def test_chat_request_too_long():
    with pytest.raises(ValidationError):
        ChatRequest(message="a" * 4097)
