

# Standard library imports
from typing import Optional

# Third-party imports
from sqlalchemy.orm import Session

# Local application imports
from app.models.user import User


class UserRepository:
    """Repository for user database operations."""
    def __init__(self, db: Session) -> None:
        """Initialize with a database session."""
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        return self.db.query(User).filter(User.email == email).first()

    def create(self, name: str, email: str, hashed_password: str) -> User:
        """Create and persist a new user."""
        user = User(name=name, email=email, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
