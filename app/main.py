from fastapi import FastAPI
from app.api import users, chat
from app.core.database import Base, engine

app = FastAPI(title="AI Chatbot API", description="A REST API for user registration, authentication, and AI chat.")

# Create tables at startup (for demo/dev)
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(chat.router, tags=["chat"])
