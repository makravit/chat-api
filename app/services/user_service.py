"""User-related business logic for registration, auth, and sessions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from typing import TYPE_CHECKING, cast

from app.core.auth import create_access_token, hash_password, verify_password
from app.core.config import settings
from app.core.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.core.logging import logger, mask_token
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository

if TYPE_CHECKING:  # pragma: no cover - types only
    from sqlalchemy.orm import Session

    from app.models.refresh_token import RefreshToken
    from app.models.user import User


def register_user(name: str, email: str, password: str, db: Session) -> User:
    """Register a new user and return the created ORM object.

    Raises EmailAlreadyRegisteredError if the email already exists.
    """
    repo = UserRepository(db)
    existing = repo.get_by_email(email)
    if existing:
        logger.warning("Registration failed: email already registered", email=email)
        msg = "Email is already registered."
        raise EmailAlreadyRegisteredError(msg)
    hashed = hash_password(password)
    new_user = repo.create(name=name, email=email, hashed_password=hashed)
    logger.info("User created", user_id=new_user.id, email=new_user.email)
    return new_user


def authenticate_user(
    email: str,
    password: str,
    db: Session,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[str, str]:
    """Authenticate a user and return access and refresh tokens.

    Raises InvalidCredentialsError if login fails.
    """
    repo = UserRepository(db)
    token_repo = RefreshTokenRepository(db)
    db_user = repo.get_by_email(email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        logger.warning("Authentication failed", email=email)
        msg = "Email or password incorrect."
        raise InvalidCredentialsError(msg)
    access_token = create_access_token({"sub": db_user.email})
    # Do not revoke all previous tokens; allow multiple sessions/devices
    # Create secure random refresh token
    refresh_token = token_urlsafe(64)
    # Configurable refresh token expiry
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_repo.add_token(
        db_user.id,
        refresh_token,
        expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    logger.info(
        "Authentication successful",
        user_id=getattr(db_user, "id", None),
        email=email,
    )
    log_refresh_token_event(
        event_type="create",
        user_id=db_user.id,
        token=refresh_token,
        user_agent=user_agent,
        ip_address=ip_address,
        details={"expires_at": expires_at.isoformat()},
    )
    return access_token, refresh_token


def logout_single_session(current_user: User, db: Session, refresh_token: str) -> None:
    """Revoke the current session's refresh token only."""
    token_repo = RefreshTokenRepository(db)
    token_obj = token_repo.get_valid_token(refresh_token)
    if not token_obj:
        logger.warning(
            "Suspicious activity: invalid or revoked refresh token used for logout",
            user_id=getattr(current_user, "id", None),
            token=mask_token(refresh_token),
        )
        log_refresh_token_event(
            event_type="suspicious",
            user_id=getattr(current_user, "id", None),
            token=mask_token(refresh_token),
            details={"reason": "invalid or revoked token used for logout"},
        )
        msg = "No active session or already logged out."
        raise InvalidCredentialsError(msg)
    if token_obj.user_id != current_user.id:
        logger.warning(
            "Suspicious activity: refresh token user mismatch on logout",
            user_id=getattr(current_user, "id", None),
            token=mask_token(refresh_token),
        )
        log_refresh_token_event(
            event_type="suspicious",
            user_id=getattr(current_user, "id", None),
            token=mask_token(refresh_token),
            details={"reason": "refresh token user mismatch on logout"},
        )
        msg = "No active session or already logged out."
        raise InvalidCredentialsError(msg)
    if token_obj.revoked:
        logger.warning(
            "Suspicious activity: revoked refresh token used for logout",
            user_id=current_user.id,
            token=mask_token(refresh_token),
        )
        log_refresh_token_event(
            event_type="suspicious",
            user_id=current_user.id,
            token=mask_token(refresh_token),
            details={"reason": "revoked token used for logout"},
        )
        msg = "No active session or already logged out."
        raise InvalidCredentialsError(msg)
    token_repo.revoke_token(refresh_token)
    logger.info(
        "Refresh token revoked on logout",
        user_id=current_user.id,
        token=mask_token(refresh_token),
    )
    log_refresh_token_event(
        event_type="revoke",
        user_id=current_user.id,
        token=refresh_token,
    )


def logout_all_sessions(current_user: User, db: Session) -> None:
    """Revoke all refresh tokens for the user (logout everywhere)."""
    token_repo = RefreshTokenRepository(db)
    token_repo.revoke_all_tokens(current_user.id)
    logger.info(
        "All refresh tokens revoked (logout everywhere)",
        user_id=current_user.id,
    )
    log_refresh_token_event(event_type="revoke_all", user_id=current_user.id)


# Helper functions for token validation and anomaly detection
def _validate_refresh_token(
    token_obj: RefreshToken | None, token: str, now: datetime
) -> None:
    """Validate refresh token object and raise if invalid/expired/revoked."""
    if not token_obj:
        logger.warning(
            "Suspicious activity: invalid or revoked refresh token used for rotation",
            token=mask_token(token),
        )
        log_refresh_token_event(
            event_type="suspicious",
            token=mask_token(token),
            details={"reason": "invalid or revoked token used for rotation"},
        )
        msg = "Invalid or expired refresh token"
        raise InvalidCredentialsError(msg)
    if token_obj.revoked:
        logger.warning(
            "Suspicious activity: revoked refresh token used for rotation",
            user_id=token_obj.user_id,
            token=mask_token(token),
        )
        log_refresh_token_event(
            event_type="suspicious",
            user_id=token_obj.user_id,
            token=mask_token(token),
            details={"reason": "revoked token used for rotation"},
        )
        msg = "Invalid or expired refresh token"
        raise InvalidCredentialsError(msg)
    if token_obj.expires_at < now:
        logger.warning(
            "Suspicious activity: expired refresh token used for rotation",
            user_id=token_obj.user_id,
            token=mask_token(token),
        )
        log_refresh_token_event(
            event_type="suspicious",
            user_id=token_obj.user_id,
            token=mask_token(token),
            details={"reason": "expired token used for rotation"},
        )
        msg = "Invalid or expired refresh token"
        raise InvalidCredentialsError(msg)


def _detect_anomalies(
    token_obj: RefreshToken,
    token: str,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> None:
    """Detect anomalies comparing provided metadata with stored values."""
    if user_agent and token_obj.user_agent and user_agent != token_obj.user_agent:
        logger.warning(
            "Suspicious activity: user agent anomaly detected during refresh",
            user_id=token_obj.user_id,
            expected=token_obj.user_agent,
            actual=user_agent,
        )
        log_refresh_token_event(
            event_type="anomaly",
            user_id=token_obj.user_id,
            token=mask_token(token),
            user_agent=user_agent,
            ip_address=ip_address,
            details={
                "expected_user_agent": token_obj.user_agent,
                "actual_user_agent": user_agent,
            },
        )
    if ip_address and token_obj.ip_address and ip_address != token_obj.ip_address:
        logger.warning(
            "Suspicious activity: IP address anomaly detected during refresh",
            user_id=token_obj.user_id,
            expected=token_obj.ip_address,
            actual=ip_address,
        )
        log_refresh_token_event(
            event_type="anomaly",
            user_id=token_obj.user_id,
            token=mask_token(token),
            user_agent=user_agent,
            ip_address=ip_address,
            details={
                "expected_ip_address": token_obj.ip_address,
                "actual_ip_address": ip_address,
            },
        )


def _create_refresh_token(
    token_repo: RefreshTokenRepository,
    user_id: int,
    expiry: datetime,
    user_agent: str | None,
    ip_address: str | None,
) -> str:
    """Create and persist a new refresh token and return its value."""
    new_refresh_token = token_urlsafe(64)
    token_repo.add_token(
        user_id,
        new_refresh_token,
        expiry,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    return new_refresh_token


def rotate_refresh_token(
    old_refresh_token: str,
    db: Session,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[str, str]:
    """Rotate a refresh token and issue a new access token and refresh token."""
    token_repo = RefreshTokenRepository(db)
    token_obj = token_repo.get_valid_token(old_refresh_token)
    now = datetime.now(UTC)
    _validate_refresh_token(token_obj, old_refresh_token, now)
    # token_obj is validated to be not None by _validate_refresh_token
    token_typed = cast("RefreshToken", token_obj)
    _detect_anomalies(token_typed, old_refresh_token, user_agent, ip_address)
    # Revoke old token (single-use)
    token_repo.revoke_token(old_refresh_token)
    log_refresh_token_event(
        event_type="rotate",
        user_id=token_typed.user_id,
        token=mask_token(old_refresh_token),
        user_agent=user_agent,
        ip_address=ip_address,
    )
    user_id = token_typed.user_id
    user_repo = UserRepository(db)
    db_user = user_repo.get_by_id(user_id)
    if not db_user:
        logger.warning(
            "Suspicious activity: user not found for refresh token",
            user_id=user_id,
        )
        log_refresh_token_event(
            event_type="suspicious",
            user_id=user_id,
            token=mask_token(old_refresh_token),
            details={"reason": "user not found for refresh token"},
        )
        msg = "User not found"
        raise InvalidCredentialsError(msg)
    access_token = create_access_token({"sub": db_user.email})
    # Sliding expiration: extend expiry on rotation, but never exceed max lifetime

    refresh_expiry_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    max_lifetime_days = settings.REFRESH_TOKEN_MAX_LIFETIME_DAYS
    # Calculate max expiry from original token creation
    max_expiry = token_typed.created_at + timedelta(days=max_lifetime_days)
    # Calculate new expiry (sliding window)
    requested_expiry = now + timedelta(days=refresh_expiry_days)
    new_expiry = min(requested_expiry, max_expiry)
    new_refresh_token = _create_refresh_token(
        token_repo,
        user_id,
        new_expiry,
        user_agent,
        ip_address,
    )
    logger.info(
        "Refresh token rotated (sliding expiration)",
        user_id=user_id,
        new_expiry=new_expiry.isoformat(),
    )
    log_refresh_token_event(
        event_type="create",
        user_id=user_id,
        token=mask_token(new_refresh_token),
        user_agent=user_agent,
        ip_address=ip_address,
        details={"expires_at": new_expiry.isoformat()},
    )
    return access_token, new_refresh_token


def log_refresh_token_event(
    event_type: str,
    user_id: int | None = None,
    token: str | None = None,
    user_agent: str | None = None,
    ip_address: str | None = None,
    details: dict[str, object] | None = None,
) -> None:
    """Log refresh token events for auditing and security.

    Args describe the event fields: event_type (e.g., create/rotate/revoke),
    user_id, token, user_agent, ip_address, and optional details.
    """
    log_entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "token": mask_token(token),
        "user_agent": user_agent,
        "ip_address": ip_address,
        "details": details or {},
    }
    # Example: log to file or stdout
    logger.info(f"RefreshTokenAudit: {log_entry}")
