"""User repository for database operations."""

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Data-access layer for ``User`` entities."""

    def __init__(self: "UserRepository", db: Session) -> None:
        """Initialize the repository with a SQLAlchemy session.

        Args:
            db: Active SQLAlchemy session.
        """
        self.db = db

    def get_by_id(self: "UserRepository", user_id: int) -> User | None:
        """Return a user by primary key.

        Args:
            user_id: The user's ID.

        Returns:
            The matching ``User`` or ``None`` if not found.
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self: "UserRepository", email: str) -> User | None:
        """Return a user by unique email address, if present.

        Args:
            email: Email to look up.

        Returns:
            The matching ``User`` or ``None`` if not found.
        """
        return self.db.query(User).filter(User.email == email).first()

    def create(
        self: "UserRepository",
        name: str,
        email: str,
        hashed_password: str,
    ) -> User:
        """Create and persist a new user record.

        Args:
            name: Display name.
            email: Unique email address.
            hashed_password: Previously hashed password string.

        Returns:
            The newly created ``User`` instance.
        """
        user = User(name=name, email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
