
# Standard library imports

# Third-party imports
from fastapi import FastAPI

# Local application imports
from app.api import users, chat, health
from app.core.database import Base, get_engine

engine = get_engine()
from app.core.exception_handlers import app_exception_handler
from app.core.exceptions import AppException

app = FastAPI(title="AI Chatbot API", description="A REST API for user registration, authentication, and AI chat.")


# API Versioning: business endpoints are under /api/v1, health check is unversioned at /health
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(health.router, tags=["health"])

# Register the global exception handler for AppException
app.add_exception_handler(AppException, app_exception_handler)
