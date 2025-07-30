
from sqlalchemy.orm import Session


class EmailAlreadyRegistered(Exception):
    """Exception raised when attempting to register an email that already exists."""
    def __init__(self, message: str = "Email is already registered."):
        super().__init__(message)


class InvalidCredentials(Exception):
    """Exception raised for invalid login credentials."""
    def __init__(self, message: str = "Email or password incorrect."):
        super().__init__(message)

from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.core.auth import hash_password, verify_password, create_access_token
from app.services.user_repository import UserRepository


def register_user(user: UserRegister, db: Session) -> UserResponse:
    """Register a new user. Raises EmailAlreadyRegistered if email exists."""
    repo = UserRepository(db)
    existing = repo.get_by_email(user.email)
    if existing:
        raise EmailAlreadyRegistered()
    hashed = hash_password(user.password)
    new_user = repo.create(name=user.name, email=user.email, hashed_password=hashed)
    return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email)


def authenticate_user(user: UserLogin, db: Session) -> TokenResponse:
    """Authenticate a user and return a token. Raises InvalidCredentials if login fails."""
    repo = UserRepository(db)
    db_user = repo.get_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise InvalidCredentials()
    token = create_access_token({"sub": db_user.email})
    return TokenResponse(access_token=token)
