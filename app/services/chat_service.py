from app.schemas.chat import ChatRequest, ChatResponse
from fastapi import HTTPException, status

MAX_MESSAGE_LENGTH = 4096

# Dummy AI bot logic

def process_chat(request: ChatRequest, user):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message must not be empty or whitespace.")
    if len(message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(status_code=400, detail="Message too long. Maximum allowed is 4096 characters. Please shorten your message.")
    # Simulate bot response
    if "hello" in message.lower():
        reply = "Hello! How can I assist you today?"
    else:
        reply = "I'm here to help! Please ask me anything."
    return ChatResponse(response=reply)
