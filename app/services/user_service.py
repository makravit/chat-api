
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.core.auth import hash_password, verify_password, create_access_token
from app.services.user_repository import UserRepository


def register_user(user: UserRegister, db: Session):
    repo = UserRepository(db)
    existing = repo.get_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered.")
    hashed = hash_password(user.password)
    new_user = repo.create(name=user.name, email=user.email, hashed_password=hashed)
    return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email)


def authenticate_user(user: UserLogin, db: Session):
    repo = UserRepository(db)
    db_user = repo.get_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Email or password incorrect.")
    token = create_access_token({"sub": db_user.email})
    return TokenResponse(access_token=token)
