from types import SimpleNamespace

import pytest

from app.api.users import (
    require_refresh_cookie_for_logout,
    require_refresh_cookie_for_refresh,
)
from app.core.exceptions import InvalidCredentialsError, LogoutNoSessionError


def _make_req(cookies: dict[str, str] | None = None) -> object:
    return SimpleNamespace(cookies=cookies or {})


def test_require_refresh_cookie_for_refresh_missing() -> None:
    req = _make_req()
    with pytest.raises(InvalidCredentialsError):
        require_refresh_cookie_for_refresh(req)  # type: ignore[arg-type]


def test_require_refresh_cookie_for_logout_missing() -> None:
    req = _make_req()
    with pytest.raises(LogoutNoSessionError):
        require_refresh_cookie_for_logout(req)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["abc", "token123"])
def test_require_refresh_cookie_present_returns_value(value: str) -> None:
    req = _make_req({"refresh_token": value})
    assert require_refresh_cookie_for_refresh(req) == value  # type: ignore[arg-type]
    assert require_refresh_cookie_for_logout(req) == value  # type: ignore[arg-type]
