"""User ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from app.models.refresh_token import RefreshToken


class User(Base):
    """User account with credentials and profile data."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    # Email must be unique
    email: Mapped[str] = mapped_column(
        String(256), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)

    # Relationship to refresh tokens (defined in refresh_token.py)
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        back_populates="user",
        cascade="save-update, merge, expunge",
    )
