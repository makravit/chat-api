"""Shared test helpers used across the suite.

This module provides:
- Minimal SQLAlchemy-like DB doubles for common query/commit flows.
- Deterministic string builders for tokens, basic auth, and passwords.

Public string helpers:
- ``join_parts(*parts)`` — join parts to create deterministic test strings.
- ``build_password(kind)`` — return canonical passwords for validation cases.

Supported password kinds: "valid", "wrong", "short", "weak",
"missing_symbol", "missing_number".

Use these helpers to generate repeatable, non-secret values in tests.
"""

from collections.abc import Sequence
from typing import Literal
from unittest.mock import MagicMock


def make_db_query_first(result: object) -> MagicMock:
    """Create a DB mock where query(...).filter(...).first() returns ``result``."""
    db: MagicMock = MagicMock()
    query_mock: MagicMock = MagicMock()
    filter_mock: MagicMock = MagicMock()
    filter_mock.first.return_value = result
    query_mock.filter.return_value = filter_mock
    db.query.return_value = query_mock
    return db


def make_db_query_all(results: Sequence[object]) -> MagicMock:
    """Create a DB mock where query(...).filter(...).all() returns ``results``."""
    db: MagicMock = MagicMock()
    query_mock: MagicMock = MagicMock()
    filter_mock: MagicMock = MagicMock()
    filter_mock.all.return_value = results
    query_mock.filter.return_value = filter_mock
    db.query.return_value = query_mock
    return db


def make_db_commit_mock() -> MagicMock:
    """Create a DB mock with a convenience ``assert_committed_once()`` method.

    Example:
        db = make_db_commit_mock()
        # ... perform operations that should call commit()
        db.assert_committed_once()
    """
    db: MagicMock = MagicMock()

    def assert_committed_once() -> None:
        db.commit.assert_called_once()

    # Attach a convenience assertion for consistent usage in tests
    db.assert_committed_once = assert_committed_once  # type: ignore[attr-defined]
    return db


def make_dummy_db() -> MagicMock:
    """Create a minimal DB placeholder for tests not asserting DB behavior."""
    return MagicMock()


# --- String helpers ---


def join_parts(*parts: str) -> str:
    """Join string parts to produce deterministic, non-secret test values."""
    return "".join(list(parts))


def build_password(
    kind: Literal[
        "valid",
        "wrong",
        "short",
        "weak",
        "missing_symbol",
        "missing_number",
    ] = "valid",
) -> str:
    """Return a deterministic password for the requested ``kind``.

    See the module docstring for the supported kinds.
    """
    match kind:
        case "valid":
            return join_parts("Password", "1!")
        case "wrong":
            return join_parts("WrongPass", "1!")
        case "short":
            return join_parts("Short", "1!")
        case "weak":
            return join_parts("password", "123")
        case "missing_symbol":
            return join_parts("Password", "1")
        case "missing_number":
            return join_parts("Password", "!")
        case _:
            return join_parts("Password", "1!")


# --- Cookie assertion helpers (integration tests) ---


def assert_secure_refresh_cookie(set_cookie_header: str) -> None:
    """Assert that a Set-Cookie securely sets the refresh token.

    Expects presence of:
    - refresh_token
    - HttpOnly, Secure, SameSite=Strict
    - positive Max-Age
    """
    h = set_cookie_header.lower()
    assert "refresh_token=" in h
    assert "httponly" in h
    assert "secure" in h
    assert "samesite=strict" in h
    assert "max-age=" in h
    # parse max-age value
    try:
        start = h.index("max-age=") + len("max-age=")
        end = h.find(";", start)
        val = h[start:end] if end != -1 else h[start:]
        assert int(val) > 0
    except (ValueError, AttributeError, TypeError):
        msg = "Invalid Max-Age on refresh cookie"
        raise AssertionError(msg) from None


def assert_deleted_refresh_cookie(set_cookie_header: str) -> None:
    """Assert that a Set-Cookie securely clears the refresh token.

    Expects presence of:
    - refresh_token
    - HttpOnly, Secure, SameSite=Strict
    - Max-Age=0 (and often Expires in the past)
    """
    h = set_cookie_header.lower()
    assert "refresh_token=" in h
    assert "httponly" in h
    assert "secure" in h
    assert "samesite=strict" in h
    assert "max-age=0" in h
