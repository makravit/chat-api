"""Request metadata utilities.

Helpers to extract common request metadata (user agent, client IP) in a
consistent and testable way.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from fastapi import Request


def get_user_agent(request: Request) -> str | None:
    """Return the User-Agent header value, if present.

    Args:
        request: FastAPI request instance.

    Returns:
        The user agent string if provided by the client, otherwise None.
    """
    return request.headers.get("user-agent")


def get_client_ip(request: Request) -> str | None:
    """Return the best-effort client IP address.

    Preference order:
    1) X-Forwarded-For (left-most address)
    2) request.client.host
    3) X-Real-IP

    Returns None if no candidate is available.
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        first = xff.split(",")[0].strip()
        if first:
            return first
    if request.client:
        return request.client.host
    return request.headers.get("x-real-ip")
