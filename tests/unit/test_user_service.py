from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import MagicMock, patch

import pytest
from jose import jwt
from sqlalchemy.exc import SQLAlchemyError

import app.core.config as cfg
from app.core.auth import ALGORITHM, SECRET_KEY, hash_password
from app.core.exceptions import (
    InvalidCredentialsError,
    LogoutNoSessionError,
    LogoutOperationError,
)

if TYPE_CHECKING:  # pragma: no cover - used for typing only
    from app.models.user import User
from app.services.user_service import (
    EmailAlreadyRegisteredError,
    authenticate_user,
    issue_access_token,
    logout_all_sessions,
    logout_single_session,
    register_user,
    rotate_refresh_token,
)
from tests.utils import PasswordKind, build_password, join_parts, make_dummy_db


# ---------- access token helper ----------
def test_issue_access_token_includes_uid_and_sub() -> None:
    user = cast("User", SimpleNamespace(id=123, email="u@e.com"))
    token = issue_access_token(user)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["uid"] == 123
    assert payload["sub"] == "u@e.com"
    assert "exp" in payload


# ---------- authenticate_user ----------
def test_authenticate_user_success() -> None:
    email = "test@example.com"
    password = build_password(PasswordKind.VALID)
    db_user = MagicMock(email=email, hashed_password=hash_password(password), id=1)
    repo_mock = MagicMock(get_by_email=MagicMock(return_value=db_user))
    token_repo_mock = MagicMock()
    with (
        patch("app.services.user_service.UserRepository", return_value=repo_mock),
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo_mock,
        ),
    ):
        access_token, refresh_token = authenticate_user(
            email,
            password,
            make_dummy_db(),
            user_agent="ua",
            ip_address="1.2.3.4",
        )
    assert isinstance(access_token, str)
    assert access_token
    assert isinstance(refresh_token, str)
    assert refresh_token
    token_repo_mock.add_token.assert_called_once()


def test_authenticate_user_triggers_rehash_on_verify(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    email = "rehash@example.com"
    password = build_password(PasswordKind.VALID)
    db_user = MagicMock(email=email, hashed_password=hash_password(password), id=42)
    repo_mock = MagicMock(get_by_email=MagicMock(return_value=db_user))
    token_repo_mock = MagicMock()
    # Force needs_rehash to return True so the helper runs
    monkeypatch.setattr("app.services.user_service.needs_rehash", lambda _h: True)
    with (
        patch("app.services.user_service.UserRepository", return_value=repo_mock),
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo_mock,
        ),
    ):
        access_token, refresh_token = authenticate_user(
            email,
            password,
            make_dummy_db(),
            user_agent="ua",
            ip_address="127.0.0.1",
        )
    assert access_token
    assert refresh_token
    # Ensure rehash persisted
    assert repo_mock.update_password.called
    args, _ = repo_mock.update_password.call_args
    assert args[0] == 42
    assert isinstance(args[1], str)
    assert args[1] != db_user.hashed_password


def test_authenticate_user_rehash_failure_does_not_block_login(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    email = "rehash-fail@example.com"
    password = build_password(PasswordKind.VALID)
    db_user = MagicMock(email=email, hashed_password=hash_password(password), id=7)
    repo_mock = MagicMock(
        get_by_email=MagicMock(return_value=db_user),
        update_password=MagicMock(side_effect=SQLAlchemyError("db write failed")),
    )
    token_repo_mock = MagicMock()
    monkeypatch.setattr("app.services.user_service.needs_rehash", lambda _h: True)
    with (
        patch("app.services.user_service.UserRepository", return_value=repo_mock),
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo_mock,
        ),
    ):
        # Should still succeed even if update_password raises
        access_token, refresh_token = authenticate_user(
            email,
            password,
            make_dummy_db(),
        )
    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)


def test_authenticate_user_wrong_password() -> None:
    email = "test@example.com"
    repo_mock = MagicMock(
        get_by_email=MagicMock(
            return_value=MagicMock(
                email=email,
                hashed_password=hash_password(build_password(PasswordKind.VALID)),
                id=1,
            ),
        ),
    )
    with (
        patch("app.services.user_service.UserRepository", return_value=repo_mock),
        pytest.raises(InvalidCredentialsError),
    ):
        authenticate_user(email, build_password(PasswordKind.WRONG), make_dummy_db())


def test_authenticate_user_not_found() -> None:
    repo_mock = MagicMock(get_by_email=MagicMock(return_value=None))
    with (
        patch("app.services.user_service.UserRepository", return_value=repo_mock),
        pytest.raises(InvalidCredentialsError),
    ):
        authenticate_user(
            "no@user",
            build_password(PasswordKind.VALID),
            make_dummy_db(),
        )


# ---------- register_user ----------
def test_register_user_success() -> None:
    name, email, pwd = "Test", "test@example.com", build_password(PasswordKind.VALID)
    created = SimpleNamespace(id=1, name=name, email=email)
    repo_mock = MagicMock(
        get_by_email=MagicMock(return_value=None),
        create=MagicMock(return_value=created),
    )
    with patch("app.services.user_service.UserRepository", return_value=repo_mock):
        result = register_user(name, email, pwd, MagicMock())
    assert result.email == email


def test_register_user_duplicate() -> None:
    repo_mock = MagicMock(get_by_email=MagicMock(return_value=MagicMock()))
    with (
        patch("app.services.user_service.UserRepository", return_value=repo_mock),
        pytest.raises(EmailAlreadyRegisteredError),
    ):
        register_user(
            "Test",
            "dupe@example.com",
            build_password(PasswordKind.VALID),
            MagicMock(),
        )


# ---------- logout_single_session ----------
def test_logout_single_session_revokes_token() -> None:
    user = cast("User", SimpleNamespace(id=1, email="logout@example.com"))
    token = SimpleNamespace(user_id=1, revoked=False)
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=token))
    with patch(
        "app.services.user_service.RefreshTokenRepository",
        return_value=token_repo,
    ):
        logout_single_session(
            user,
            make_dummy_db(),
            refresh_token=join_parts("rtok"),
        )
    token_repo.revoke_token.assert_called_once_with(join_parts("rtok"))


def test_logout_single_session_revoked_token() -> None:
    user = cast("User", SimpleNamespace(id=1))
    token_repo = MagicMock(
        get_valid_token=MagicMock(
            return_value=SimpleNamespace(user_id=1, revoked=True),
        ),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        pytest.raises(LogoutNoSessionError),
    ):
        logout_single_session(
            user,
            make_dummy_db(),
            refresh_token=join_parts("rtok"),
        )


def test_logout_single_session_user_mismatch() -> None:
    user = cast("User", SimpleNamespace(id=2))
    token_repo = MagicMock(
        get_valid_token=MagicMock(
            return_value=SimpleNamespace(user_id=1, revoked=False),
        ),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        pytest.raises(LogoutNoSessionError),
    ):
        logout_single_session(
            user,
            make_dummy_db(),
            refresh_token=join_parts("rtok"),
        )


def test_logout_db_error_fetch_translates_to_logout_operation_error() -> None:
    user = cast("User", SimpleNamespace(id=1))
    token_repo = MagicMock(
        get_valid_token=MagicMock(side_effect=SQLAlchemyError("db boom")),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        pytest.raises(LogoutOperationError),
    ):
        logout_single_session(
            user,
            make_dummy_db(),
            refresh_token=join_parts("rtok"),
        )


def test_logout_db_error_revoke_translates_to_logout_operation_error() -> None:
    user = cast("User", SimpleNamespace(id=1))
    token_repo = MagicMock(
        get_valid_token=MagicMock(
            return_value=SimpleNamespace(user_id=1, revoked=False),
        ),
        revoke_token=MagicMock(side_effect=SQLAlchemyError("db boom")),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        pytest.raises(LogoutOperationError),
    ):
        logout_single_session(
            user,
            make_dummy_db(),
            refresh_token=join_parts("rtok"),
        )


# ---------- logout_all_sessions ----------
def test_logout_all_sessions_calls_repo() -> None:
    user = cast("User", SimpleNamespace(id=99))
    token_repo = MagicMock()
    with patch(
        "app.services.user_service.RefreshTokenRepository",
        return_value=token_repo,
    ):
        logout_all_sessions(user, make_dummy_db())
    token_repo.revoke_all_tokens.assert_called_once_with(99)


# ---------- rotate_refresh_token ----------
def _build_token(
    user_id: int = 1,
    revoked: bool = False,
    expires_delta: timedelta = timedelta(minutes=10),
    created_delta: timedelta = timedelta(minutes=0),
    ua: str = "ua",
    ip: str = "1.1.1.1",
) -> SimpleNamespace:
    now = datetime.now(UTC)
    return SimpleNamespace(
        user_id=user_id,
        revoked=revoked,
        expires_at=now + expires_delta,
        created_at=now + created_delta,
        user_agent=ua,
        ip_address=ip,
    )


def test_rotate_refresh_token_invalid() -> None:
    # No valid token found -> InvalidCredentialsError
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=None))
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        pytest.raises(InvalidCredentialsError),
    ):
        rotate_refresh_token("badtoken", make_dummy_db())


def test_rotate_refresh_token_revoked() -> None:
    token_repo = MagicMock(
        get_valid_token=MagicMock(return_value=_build_token(revoked=True)),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        pytest.raises(InvalidCredentialsError),
    ):
        rotate_refresh_token("old", make_dummy_db())


def test_rotate_refresh_token_expired() -> None:
    token_repo = MagicMock(
        get_valid_token=MagicMock(
            return_value=_build_token(expires_delta=timedelta(minutes=-1)),
        ),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        pytest.raises(InvalidCredentialsError),
    ):
        rotate_refresh_token("old", make_dummy_db())


def test_rotate_refresh_token_user_not_found() -> None:
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=_build_token()))
    user_repo = MagicMock(get_by_id=MagicMock(return_value=None))
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        patch("app.services.user_service.UserRepository", return_value=user_repo),
        pytest.raises(InvalidCredentialsError),
    ):
        rotate_refresh_token("old", make_dummy_db())


def test_rotate_refresh_token_success_and_single_use() -> None:
    valid = _build_token(user_id=1, ua="test-agent", ip="127.0.0.1")
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=valid))
    user_repo = MagicMock(
        get_by_id=MagicMock(return_value=SimpleNamespace(id=1, email="e@x.com")),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        patch("app.services.user_service.UserRepository", return_value=user_repo),
    ):
        atok, rtok = rotate_refresh_token(
            "oldtoken",
            make_dummy_db(),
            user_agent="test-agent",
            ip_address="127.0.0.1",
        )
    assert isinstance(atok, str)
    assert isinstance(rtok, str)
    token_repo.revoke_token.assert_called_once_with("oldtoken")
    token_repo.add_token.assert_called_once()
    # Validate user agent and IP propagated to add_token
    _, kwargs = token_repo.add_token.call_args
    assert kwargs.get("user_agent") == "test-agent"
    assert kwargs.get("ip_address") == "127.0.0.1"


def test_rotate_refresh_token_anomaly_logs_but_succeeds(
    caplog: pytest.LogCaptureFixture,
) -> None:
    valid = _build_token(user_id=1, ua="expected", ip="1.2.3.4")
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=valid))
    user_repo = MagicMock(
        get_by_id=MagicMock(return_value=SimpleNamespace(id=1, email="e@x.com")),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        patch("app.services.user_service.UserRepository", return_value=user_repo),
    ):
        caplog.set_level("WARNING")
        atok, rtok = rotate_refresh_token(
            "old",
            make_dummy_db(),
            user_agent="unexpected",
            ip_address="9.8.7.6",
        )
    assert isinstance(atok, str)
    assert isinstance(rtok, str)
    assert token_repo.revoke_token.called
    # Two warnings expected: UA anomaly and IP anomaly
    warnings = [rec for rec in caplog.records if rec.levelname == "WARNING"]
    # We can't rely on exact message text from structlog JSON,
    # but ensure at least two WARNINGs logged
    assert len(warnings) >= 2


def test_rotate_refresh_token_sliding_expiration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # created 9 days ago, expire window 7 days,
    # max lifetime 10 days -> new expiry
    # should be <= created+10d
    valid = _build_token(created_delta=timedelta(days=-9))
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=valid))
    user_repo = MagicMock(
        get_by_id=MagicMock(return_value=SimpleNamespace(id=1, email="e@x.com")),
    )
    # Patch settings

    monkeypatch.setattr(cfg.settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)
    monkeypatch.setattr(cfg.settings, "REFRESH_TOKEN_MAX_LIFETIME_DAYS", 10)
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        patch("app.services.user_service.UserRepository", return_value=user_repo),
    ):
        rotate_refresh_token("old", make_dummy_db())
    # Assert add_token called with expiry <= created_at + max_lifetime
    assert token_repo.add_token.called
    args, _ = token_repo.add_token.call_args
    # add_token signature:
    # (user_id, token, expires_at,
    #  optional user_agent, optional ip_address)
    new_expiry = args[2]
    assert new_expiry <= valid.created_at + timedelta(days=10)


def test_rotate_refresh_token_anomaly_ip_only_logs_but_succeeds(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """If only IP mismatches, rotation still succeeds (anomaly is logged)."""
    valid = _build_token(user_id=1, ua="expected", ip="1.2.3.4")
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=valid))
    user_repo = MagicMock(
        get_by_id=MagicMock(return_value=SimpleNamespace(id=1, email="e@x.com")),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        patch("app.services.user_service.UserRepository", return_value=user_repo),
    ):
        caplog.set_level("WARNING")
        atok, rtok = rotate_refresh_token(
            "old",
            make_dummy_db(),
            user_agent="expected",  # matches
            ip_address="9.9.9.9",  # mismatch
        )
    assert isinstance(atok, str)
    assert isinstance(rtok, str)
    token_repo.revoke_token.assert_called_once_with("old")
    token_repo.add_token.assert_called_once()
    warnings = [rec for rec in caplog.records if rec.levelname == "WARNING"]
    assert len(warnings) >= 1


def test_rotate_refresh_token_no_metadata_provided_succeeds() -> None:
    """Rotation succeeds even if client omits UA/IP; no anomaly should be triggered."""
    valid = _build_token(user_id=1, ua="some-ua", ip="10.0.0.1")
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=valid))
    user_repo = MagicMock(
        get_by_id=MagicMock(return_value=SimpleNamespace(id=1, email="e@x.com")),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        patch("app.services.user_service.UserRepository", return_value=user_repo),
    ):
        atok, rtok = rotate_refresh_token(
            "old",
            make_dummy_db(),
            user_agent=None,
            ip_address=None,
        )
    assert isinstance(atok, str)
    assert isinstance(rtok, str)
    token_repo.revoke_token.assert_called_once_with("old")
    token_repo.add_token.assert_called_once()


def test_rotate_refresh_token_anomaly_ua_only_logs_but_succeeds(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """If only UA mismatches, rotation still succeeds (anomaly is logged)."""
    valid = _build_token(user_id=1, ua="expected", ip="1.2.3.4")
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=valid))
    user_repo = MagicMock(
        get_by_id=MagicMock(return_value=SimpleNamespace(id=1, email="e@x.com")),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository",
            return_value=token_repo,
        ),
        patch("app.services.user_service.UserRepository", return_value=user_repo),
    ):
        caplog.set_level("WARNING")
        atok, rtok = rotate_refresh_token(
            "old",
            make_dummy_db(),
            user_agent="unexpected",  # mismatch
            ip_address="1.2.3.4",  # matches
        )
    assert isinstance(atok, str)
    assert isinstance(rtok, str)
    token_repo.revoke_token.assert_called_once_with("old")
    token_repo.add_token.assert_called_once()
    warnings = [rec for rec in caplog.records if rec.levelname == "WARNING"]
    assert len(warnings) >= 1


def test_rotate_refresh_token_sliding_within_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When max lifetime is not limiting, expiry should be now + EXPIRE_DAYS."""
    # Fix 'now' used inside app.services.user_service
    fixed_now = datetime(2025, 1, 1, tzinfo=UTC)

    class FixedDatetime(datetime):  # type: ignore[misc]
        @classmethod
        def now(cls, tz: object | None = None) -> datetime:  # pragma: no cover - shim
            return fixed_now if tz is None else fixed_now.astimezone(tz)  # type: ignore[arg-type]

    monkeypatch.setattr("app.services.user_service.datetime", FixedDatetime)

    # Configure settings: EXPIRE=7 days, MAX_LIFETIME=30 days
    monkeypatch.setattr(cfg.settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)
    monkeypatch.setattr(cfg.settings, "REFRESH_TOKEN_MAX_LIFETIME_DAYS", 30)

    # Token created 1 day ago, not near max lifetime
    valid_token = SimpleNamespace(
        user_id=1,
        revoked=False,
        expires_at=fixed_now + timedelta(minutes=10),
        created_at=fixed_now - timedelta(days=1),
        user_agent=None,
        ip_address=None,
    )
    token_repo = MagicMock(get_valid_token=MagicMock(return_value=valid_token))
    user_repo = MagicMock(
        get_by_id=MagicMock(return_value=SimpleNamespace(id=1, email="e@x.com")),
    )
    with (
        patch(
            "app.services.user_service.RefreshTokenRepository", return_value=token_repo
        ),
        patch("app.services.user_service.UserRepository", return_value=user_repo),
    ):
        rotate_refresh_token("old", make_dummy_db())
    assert token_repo.add_token.called
    args, _ = token_repo.add_token.call_args
    new_expiry = args[2]
    assert new_expiry == fixed_now + timedelta(days=7)
