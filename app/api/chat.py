"""Chat API endpoints.

Provides a simple chat route that echoes a helpful response.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.core.logging import logger
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import process_chat

router = APIRouter(tags=["Chat"])


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat endpoint",
    description="Process a chat request and return a response.",
    response_description="The chat response.",
)
def chat(
    request: ChatRequest,
    user: Annotated[User, Depends(get_current_user)],
) -> ChatResponse:
    """Process a chat request for the authenticated user.

    Args:
        request: Request body containing the user's message.
        user: The authenticated user extracted from the access token.

    Returns:
        A chat response produced by the service layer.
    """
    logger.info(
        "Chat request",
        user_id=getattr(user, "id", None),
        email=getattr(user, "email", None),
    )
    return process_chat(request, user)
