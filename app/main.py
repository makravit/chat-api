
# Standard library imports

# Third-party imports
from fastapi import FastAPI

# Local application imports
from app.api import users, chat, health
from app.core.database import Base, engine
from app.core.exception_handlers import app_exception_handler
from app.core.exceptions import AppException

app = FastAPI(title="AI Chatbot API", description="A REST API for user registration, authentication, and AI chat.")

# Create tables at startup (for demo/dev)
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

# API Versioning: business endpoints are under /api/v1, health check is unversioned at /health
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(health.router, tags=["health"])

# Register the global exception handler for AppException
app.add_exception_handler(AppException, app_exception_handler)
