"""Authentication and authorization helpers.

Includes password hashing/verification, JWT access token creation, refresh
token creation, OAuth2 bearer dependency, and a Basic Auth guard used by the
metrics endpoint.
"""

import secrets
from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")
security = HTTPBasic()


def hash_password(password: str) -> str:
    """Hash a plaintext password using a secure algorithm (bcrypt)."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify that a plaintext password matches a stored hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: Mapping[str, object]) -> str:
    """Create a signed JWT access token with expiration.

    Args:
        data: Claims to embed (e.g., {"sub": email}).

    Returns:
        Encoded JWT string.
    """
    # Ensure we operate on a concrete dict for mutation regardless of Mapping type
    to_encode: dict[str, object] = dict(data)
    expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token() -> tuple[str, datetime]:
    """Create an opaque refresh token and its expiration timestamp."""
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token = secrets.token_urlsafe(64)
    return token, expire


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Retrieve the current user from the bearer token.

    Decodes the JWT, extracts the subject (email), and fetches the user from
    the database. Raises 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Please log in or register.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid_value = payload.get("uid")
        if not isinstance(uid_value, int):
            raise credentials_exception
        uid: int = uid_value
    except JWTError:
        raise credentials_exception from None
    user = db.query(User).filter(User.id == uid).first()
    if user is None:
        raise credentials_exception
    return user


def basic_auth_guard(username: str, password: str) -> Callable[..., None]:
    """Return a FastAPI dependency that enforces HTTP Basic auth.

    Args:
        username: Expected username.
        password: Expected password.

    Returns:
        A dependency function that raises 401 if credentials do not match.
    """

    def _guard(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> None:
        correct_username = secrets.compare_digest(credentials.username, username)
        correct_password = secrets.compare_digest(credentials.password, password)
        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

    return _guard
