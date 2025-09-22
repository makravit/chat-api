"""User repository service wrapper.

This module provides a repository abstraction for basic user CRUD operations.
"""

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository for user database operations."""

    def __init__(self: "UserRepository", db: Session) -> None:
        """Initialize with a database session."""
        self.db = db

    def get_by_email(self: "UserRepository", email: str) -> User | None:
        """Get a user by email address."""
        return self.db.query(User).filter(User.email == email).first()

    def create(
        self: "UserRepository",
        name: str,
        email: str,
        hashed_password: str,
    ) -> User:
        """Create and persist a new user."""
        user = User(name=name, email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
