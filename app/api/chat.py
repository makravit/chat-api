from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_chat
from app.core.auth import get_current_user

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user=Depends(get_current_user)):
    return process_chat(request, user)
