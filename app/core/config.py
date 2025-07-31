
# Standard library imports

# Third-party imports
from pydantic_settings import BaseSettings

# Local application imports


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://chatbot:chatbotpass@db:5432/chatbotdb"
    SECRET_KEY: str = "secret-key"
    LOG_LEVEL: str = "INFO"  # Configurable log level, e.g., DEBUG, INFO, WARNING, ERROR
    # Add more config variables as needed

    class Config:
        env_file = ".env"

settings = Settings()
