from typing import Any
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatRequest
from app.services.chat_service import process_chat


@pytest.mark.parametrize(
    ("message", "expected_error"),
    [
        ("Hello!", None),
        ("   ", "empty"),
        ("a" * 4097, "too long"),
    ],
)
def test_process_chat_cases(message: str, expected_error: str | None) -> None:
    user: Any = Mock()
    if expected_error:
        with pytest.raises(ValidationError) as exc:
            ChatRequest(message=message)
        assert expected_error in str(exc.value)
    else:
        req = ChatRequest(message=message)
        resp = process_chat(req, user)
        assert "Hello" in resp.response or "help" in resp.response
