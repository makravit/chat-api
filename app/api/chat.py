
# Standard library imports


# Third-party imports
from fastapi import APIRouter, Depends

# Local application imports
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_chat
from app.core.logging import logger
from app.core.auth import get_current_user

router = APIRouter(tags=["Chat"])

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat endpoint",
    description="Process a chat request and return a response.",
    response_description="The chat response."
)
def chat(request: ChatRequest, user=Depends(get_current_user)):
    logger.info("Chat request", user_id=getattr(user, 'id', None), email=getattr(user, 'email', None))
    return process_chat(request, user)
