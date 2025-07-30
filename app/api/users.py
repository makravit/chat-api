
from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.user_service import register_user, authenticate_user, EmailAlreadyRegistered, InvalidCredentials, AppException
from app.core.database import get_db


router = APIRouter()


# Register the exception handler for AppException
from app.core.exception_handlers import app_exception_handler
router.add_exception_handler(AppException, app_exception_handler)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    try:
        new_user = register_user(user.name, user.email, user.password, db)
        return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email)
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=409, detail="Email is already registered.")

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        token = authenticate_user(user.email, user.password, db)
        return TokenResponse(access_token=token)
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Email or password incorrect.")
