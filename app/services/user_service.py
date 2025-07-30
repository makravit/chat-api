from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.core.auth import hash_password, verify_password, create_access_token
from fastapi import HTTPException, status
from typing import Dict

# In-memory user "database"
users_db: Dict[str, User] = {}
user_id_seq = 1

def register_user(user: UserRegister):
    global user_id_seq
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email is already registered.")
    hashed = hash_password(user.password)
    new_user = User(id=user_id_seq, name=user.name, email=user.email, hashed_password=hashed)
    users_db[user.email] = new_user
    user_id_seq += 1
    return UserResponse(id=new_user.id, name=new_user.name, email=new_user.email)

def authenticate_user(user: UserLogin):
    db_user = users_db.get(user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Email or password incorrect.")
    token = create_access_token({"sub": db_user.email})
    return TokenResponse(access_token=token)
