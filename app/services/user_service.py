
from sqlalchemy.orm import Session



from app.core.exceptions import AppException, EmailAlreadyRegistered, InvalidCredentials

from app.models.user import User
from app.core.auth import hash_password, verify_password, create_access_token
from app.services.user_repository import UserRepository


def register_user(name: str, email: str, password: str, db: Session) -> User:
    """Register a new user. Raises EmailAlreadyRegistered if email exists. Returns ORM User object."""
    repo = UserRepository(db)
    existing = repo.get_by_email(email)
    if existing:
        raise EmailAlreadyRegistered()
    hashed = hash_password(password)
    new_user = repo.create(name=name, email=email, hashed_password=hashed)
    return new_user


def authenticate_user(email: str, password: str, db: Session) -> str:
    """Authenticate a user and return a JWT token string. Raises InvalidCredentials if login fails."""
    repo = UserRepository(db)
    db_user = repo.get_by_email(email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise InvalidCredentials()
    token = create_access_token({"sub": db_user.email})
    return token
