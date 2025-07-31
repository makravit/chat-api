
# Standard library imports

# Third-party imports
from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.orm import Session

# Local application imports
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.user_service import register_user, authenticate_user, EmailAlreadyRegistered, InvalidCredentials, AppException
from app.core.logging import logger
from app.core.database import get_db


router = APIRouter()




@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    new_user = register_user(user.name, user.email, user.password, db)
    logger.info("User registered", user_id=new_user.id, email=new_user.email)
    return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email)

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    token = authenticate_user(user.email, user.password, db)
    logger.info("User login", email=user.email)
    return TokenResponse(access_token=token)
