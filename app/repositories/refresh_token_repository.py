"""Repository for managing refresh token persistence and queries."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """Data access methods for refresh tokens."""

    def __init__(self: "RefreshTokenRepository", db: Session) -> None:
        """Initialize with a DB session."""
        self.db = db

    def revoke_token(self: "RefreshTokenRepository", token: str) -> None:
        """Mark a single refresh token as revoked."""
        self.db.query(RefreshToken).filter(
            RefreshToken.token == token,
            ~RefreshToken.revoked,
        ).update({"revoked": True})
        self.db.commit()

    def revoke_all_tokens(self: "RefreshTokenRepository", user_id: int) -> None:
        """Revoke all active refresh tokens for a user."""
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            ~RefreshToken.revoked,
        ).update({"revoked": True})
        self.db.commit()

    def add_token(
        self: "RefreshTokenRepository",
        user_id: int,
        token: str,
        expires_at: datetime,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        """Persist a new refresh token with metadata."""
        # Ensure expires_at is offset-aware
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        new_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=False,
            created_at=datetime.now(UTC),
            user_agent=user_agent,
            ip_address=ip_address,
        )
        self.db.add(new_token)
        self.db.commit()

    def get_valid_token(
        self: "RefreshTokenRepository",
        token: str,
    ) -> RefreshToken | None:
        """Return a non-revoked token by value, or None if not found."""
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token == token, ~RefreshToken.revoked)
            .first()
        )

    def get_valid_tokens(
        self: "RefreshTokenRepository",
        user_id: int,
    ) -> list[RefreshToken]:
        """Return all non-revoked tokens for a given user id."""
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id, ~RefreshToken.revoked)
            .all()
        )
