
from app.schemas.chat import ChatRequest, ChatResponse

# Dummy AI bot logic

def process_chat(request: ChatRequest, user):
    # Pydantic already validates message content and length
    message = request.message.strip()
    # Simulate bot response
    if "hello" in message.lower():
        reply = "Hello! How can I assist you today?"
    else:
        reply = "I'm here to help! Please ask me anything."
    return ChatResponse(response=reply)
