"""App configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration sourced from environment variables.

    Values can be overridden via an .env file or process environment. See
    `model_config` for the location of the .env file.
    """

    DATABASE_URL: str = "postgresql://chatbot:chatbotpass@db:5432/chatbotdb"
    SECRET_KEY: str = "secret-key"
    LOG_LEVEL: str = "INFO"  # Configurable log level, e.g., DEBUG, INFO, WARNING, ERROR
    METRICS_USER: str = "metrics"
    METRICS_PASS: str = "metrics"
    JWT_EXPIRE_MINUTES: int = 15  # JWT expiration in minutes (default: 15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1
    REFRESH_TOKEN_MAX_LIFETIME_DAYS: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
