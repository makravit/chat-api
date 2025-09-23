from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:  # pragma: no cover - typing-only import
    from fastapi import Request

from app.core.request_utils import get_client_ip, get_user_agent


def test_get_user_agent_present() -> None:
    req = cast(
        "Request",
        SimpleNamespace(headers={"user-agent": "pytest-agent/1.0"}, client=None),
    )
    assert get_user_agent(req) == "pytest-agent/1.0"


def test_get_user_agent_missing() -> None:
    req = cast("Request", SimpleNamespace(headers={}, client=None))
    assert get_user_agent(req) is None


def test_get_client_ip_prefers_x_forwarded_for() -> None:
    req = cast(
        "Request",
        SimpleNamespace(
            headers={"x-forwarded-for": "1.2.3.4, 5.6.7.8"},
            client=SimpleNamespace(host="9.9.9.9"),
        ),
    )
    assert get_client_ip(req) == "1.2.3.4"


def test_get_client_ip_falls_back_to_client_host() -> None:
    req = cast(
        "Request",
        SimpleNamespace(headers={}, client=SimpleNamespace(host="203.0.113.10")),
    )
    assert get_client_ip(req) == "203.0.113.10"


def test_get_client_ip_uses_x_real_ip_when_no_client() -> None:
    req = cast(
        "Request", SimpleNamespace(headers={"x-real-ip": "198.51.100.22"}, client=None)
    )
    assert get_client_ip(req) == "198.51.100.22"


def test_get_client_ip_returns_none_when_unavailable() -> None:
    req = cast("Request", SimpleNamespace(headers={}, client=None))
    assert get_client_ip(req) is None
