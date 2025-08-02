
# Standard library imports

from app.core.database import get_db
from app.core.logging import logger

# Local application imports
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.user_service import authenticate_user, register_user

# Third-party imports
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=["Users"])

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Register a new user with name, email, and password. All fields are required. Email must be unique and valid. Password must be at least 8 characters, contain letters, numbers, and at least one symbol (!@#$%^&*).
    """,
    response_description="The registered user.",
    tags=["Users"]
)
def register(
    user: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user. Returns the created user on success.
    """
    new_user = register_user(user.name, user.email, user.password, db)
    logger.info("User registered", user_id=new_user.id, email=new_user.email)
    return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and get JWT token",
    description="""
    Authenticate a user with email and password. Returns a JWT access token on success. Both fields are required. If credentials are incorrect, a generic error message is returned.
    """,
    response_description="JWT access token.",
    tags=["Users"]
)
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return a JWT token. Returns a JWT access token on success.
    """
    token = authenticate_user(user.email, user.password, db)
    logger.info("User login", email=user.email)
    return TokenResponse(access_token=token, token_type="bearer")
