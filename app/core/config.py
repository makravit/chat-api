
# Standard library imports

# Third-party imports
from pydantic_settings import BaseSettings

# Local application imports

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://chatbot:chatbotpass@db:5432/chatbotdb"
    POSTGRES_USER: str = "chatbot"
    POSTGRES_PASSWORD: str = "chatbotpass"
    POSTGRES_DB: str = "chatbotdb"
    SECRET_KEY: str = "secret-key"
    LOG_LEVEL: str = "INFO"  # Configurable log level, e.g., DEBUG, INFO, WARNING, ERROR

    class Config:
        env_file = ".env"

settings = Settings()
