
import pytest
from pydantic import ValidationError
from app.services.chat_service import process_chat
from app.schemas.chat import ChatRequest

class DummyUser:
    pass

def test_process_chat_happy():
    req = ChatRequest(message="Hello!")
    user = DummyUser()
    resp = process_chat(req, user)
    assert "Hello" in resp.response or "help" in resp.response


def test_process_chat_empty():
    with pytest.raises(ValidationError) as exc:
        ChatRequest(message="   ")
    assert "empty" in str(exc.value)


def test_process_chat_too_long():
    with pytest.raises(ValidationError) as exc:
        ChatRequest(message="a" * 4097)
    assert "too long" in str(exc.value)
