
# Standard library imports

# Third-party imports
from sqlalchemy.orm import Session

# Local application imports
from app.core.exceptions import AppException, EmailAlreadyRegistered, InvalidCredentials
from app.models.user import User
from app.core.auth import hash_password, verify_password, create_access_token
from app.services.user_repository import UserRepository
from app.core.logging import logger

def register_user(name: str, email: str, password: str, db: Session) -> User:
    """Register a new user. Raises EmailAlreadyRegistered if email exists. Returns ORM User object."""
    repo = UserRepository(db)
    existing = repo.get_by_email(email)
    if existing:
        logger.warning("Registration failed: email already registered", email=email)
        raise EmailAlreadyRegistered()
    hashed = hash_password(password)
    new_user = repo.create(name=name, email=email, hashed_password=hashed)
    logger.info("User created", user_id=new_user.id, email=new_user.email)
    return new_user

def authenticate_user(email: str, password: str, db: Session) -> str:
    """Authenticate a user and return a JWT token string. Raises InvalidCredentials if login fails."""
    repo = UserRepository(db)
    db_user = repo.get_by_email(email)
    if not db_user or not verify_password(password, db_user.hashed_password):
        logger.warning("Authentication failed", email=email)
        raise InvalidCredentials()
    token = create_access_token({"sub": db_user.email})
    logger.info("Authentication successful", user_id=getattr(db_user, 'id', None), email=email)
    return token
