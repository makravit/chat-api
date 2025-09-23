"""User authentication and session management endpoints.

Provides registration, login (JWT access + refresh), token refresh with
rotation and sliding expiration, and logout flows.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import InvalidCredentialsError, LogoutOperationError
from app.core.logging import logger
from app.models.user import User
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services import user_service

router = APIRouter(tags=["Users"])


# Shared constants for cookie name and generic messages
REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_INVALID_MSG = "Invalid or expired refresh token."
LOGOUT_GENERIC_MSG = "No active session or already logged out."


# Internal helpers to keep cookie logic and retrieval DRY
def _cookie_max_age() -> int:
    """Return refresh cookie max_age in seconds based on settings."""
    return settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def _set_refresh_cookie(response: Response, value: str) -> None:
    """Set the refresh_token cookie with secure defaults.

    Args:
        response: The response object to mutate.
        value: The refresh token value to set.
    """
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=value,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=_cookie_max_age(),
    )


def _get_refresh_cookie(request: Request) -> str | None:
    """Return the refresh_token cookie value if present, else None."""
    return request.cookies.get(REFRESH_COOKIE_NAME)


def _clear_refresh_cookie(response: Response) -> None:
    """Remove the refresh token cookie from the client."""
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        secure=True,
        samesite="strict",
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Register a new user with name, email, and password. All fields are required.
    Email must be unique and valid. Password must be at least 8 characters,
    contain letters, numbers, and at least one symbol (!@#$%^&*).
    """,
    response_description="The registered user.",
)
def register(
    user: UserRegister,
    db: Annotated[Session, Depends(get_db)],
) -> UserResponse:
    """Register a new user.

    Args:
        user: Registration payload containing name, email and password.
        db: Database session dependency.

    Returns:
        The created user (id, name, email).
    """
    new_user = user_service.register_user(user.name, user.email, user.password, db)
    logger.info("User registered", user_id=new_user.id, email=new_user.email)
    return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and get JWT token",
    description="""
    Authenticate a user with email and password. Returns a JWT access token on
    success. Both fields are required. If credentials are incorrect, a generic
    error message is returned.
    """,
    response_description="JWT access token.",
)
def login(
    user: UserLogin,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Authenticate a user and set a refresh cookie.

    Args:
        user: Login payload with email and password.
        response: Response used to set the refresh token cookie.
        db: Database session dependency.

    Returns:
        A JWT access token response.
    """
    access_token, refresh_token = user_service.authenticate_user(
        user.email,
        user.password,
        db,
    )
    logger.info("User login", email=user.email)
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post(
    "/refresh-token",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="""
    Use a valid refresh token to obtain a new access token and refresh token.
    Previous refresh token is invalidated.
    """,
)
def refresh_token(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Refresh the access token using a valid refresh token.

    Rotates the refresh token with sliding expiration and sets the new value in
    a secure cookie.
    """
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    refresh_token_value = _get_refresh_cookie(request)
    if not refresh_token_value:
        logger.warning("Refresh token failed: missing token")
        raise HTTPException(status_code=401, detail=REFRESH_INVALID_MSG)
    try:
        access_token, new_refresh_token = user_service.rotate_refresh_token(
            refresh_token_value,
            db,
            user_agent=user_agent,
            ip_address=ip_address,
        )
    except InvalidCredentialsError as e:
        logger.warning("Refresh token failed", error=str(e))
        raise HTTPException(status_code=401, detail=REFRESH_INVALID_MSG) from None
    else:
        logger.info("Refresh token rotated")
        _set_refresh_cookie(response, new_refresh_token)
        return TokenResponse(access_token=access_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user and revoke refresh token",
    description="""
    Logout the authenticated user and revoke their refresh token. The operation
    is idempotent and returns 204 even if no valid session is present.
    """,
)
def logout(
    request: Request,
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Logout the authenticated user and revoke their refresh token.

    Idempotent: returns 204 even if the refresh cookie is missing/invalid.
    """
    refresh_token_value = _get_refresh_cookie(request)
    if not refresh_token_value:
        logger.warning(
            "Logout: no refresh token cookie found",
            user_id=current_user.id,
            email=current_user.email,
        )
        _clear_refresh_cookie(response)
        return
    try:
        user_service.logout_single_session(
            current_user,
            db,
            refresh_token=refresh_token_value,
        )
    except InvalidCredentialsError as e:
        # Treat invalid/expired tokens as already logged-out.
        logger.warning(
            "Logout: invalid refresh token treated as logged-out",
            user_id=current_user.id,
            email=current_user.email,
            error=str(e),
        )
    except LogoutOperationError as e:
        # Idempotent behavior: unexpected logout errors still result in 204.
        logger.exception(
            "Logout: unexpected error treated as logged-out",
            user_id=current_user.id,
            email=current_user.email,
            error=str(e),
        )
    logger.info(
        "User logged out",
        user_id=current_user.id,
        email=current_user.email,
    )
    _clear_refresh_cookie(response)
    return


@router.post(
    "/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout everywhere (revoke all refresh tokens)",
    description="""
    Logout the authenticated user from all sessions/devices by revoking all
    refresh tokens. No input required; user is identified via access token. If
    no valid refresh token exists, returns 401 Unauthorized.
    """,
)
def logout_all(
    response: Response,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    """Logout the user everywhere by revoking all refresh tokens."""
    user_service.logout_all_sessions(current_user, db)
    logger.info(
        "User logged out everywhere",
        user_id=current_user.id,
        email=current_user.email,
    )
    _clear_refresh_cookie(response)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Retrieve my user profile",
    description="Return the authenticated user's profile (id, name, email).",
    response_description="The authenticated user's profile.",
)
def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Return the current authenticated user's profile.

    Requires a valid Bearer access token. If the token is missing or invalid,
    a 401 Unauthorized is returned by the dependency.
    """
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
    )
