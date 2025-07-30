
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.user_service import register_user, authenticate_user, EmailAlreadyRegistered, InvalidCredentials
from app.core.database import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    try:
        return register_user(user, db)
    except EmailAlreadyRegistered:
        raise HTTPException(status_code=409, detail="Email is already registered.")

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        return authenticate_user(user, db)
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Email or password incorrect.")
