"""Chat service with simple heuristic responses."""

from app.schemas.chat import ChatRequest, ChatResponse


def process_chat(request: ChatRequest, _user: object) -> ChatResponse:
    """Process a chat request and return a bot response.

    A minimal, deterministic implementation for demonstration and testing.
    """
    message = request.message.strip()
    if "hello" in message.lower():
        reply = "Hello! How can I assist you today?"
    else:
        reply = "I'm here to help! Please ask me anything."
    return ChatResponse(response=reply)
