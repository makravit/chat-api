from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.user_service import register_user, authenticate_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister):
    return register_user(user)

@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    return authenticate_user(user)
