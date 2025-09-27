"""App configuration settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration sourced from environment variables.

    Values can be overridden via an .env file or process environment. See
    `model_config` for the location of the .env file.
    """

    # Database connection (component variables)
    # Defaults are suitable for Docker Compose. Override in local dev via .env.
    DATABASE_HOST: str = "db"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "chatbot"
    DATABASE_PASSWORD: str = "chatbotpass"
    DATABASE_NAME: str = "chatbotdb"

    SECRET_KEY: str = "secret-key"
    LOG_LEVEL: str = "INFO"  # Configurable log level, e.g., DEBUG, INFO, WARNING, ERROR
    METRICS_USER: str = "metrics"
    METRICS_PASS: str = "metrics"
    JWT_EXPIRE_MINUTES: int = 15  # JWT expiration in minutes (default: 15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 1
    REFRESH_TOKEN_MAX_LIFETIME_DAYS: int = 30
    ARGON2_TIME_COST: int = 3
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 2

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def database_url(self) -> str:
        """Assemble and return the SQLAlchemy database URL for PostgreSQL.

        The URL is constructed from the component variables so that callers
        don't need to repeat the assembly logic across the codebase.
        """
        user = self.DATABASE_USER
        pwd = self.DATABASE_PASSWORD
        host = self.DATABASE_HOST
        port = self.DATABASE_PORT
        name = self.DATABASE_NAME
        return f"postgresql://{user}:{pwd}@{host}:{port}/{name}"


settings = Settings()
