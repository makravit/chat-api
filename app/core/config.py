from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://chatbot:chatbotpass@db:5432/chatbotdb"
    TEST_DATABASE_URL: str = "postgresql://chatbot:chatbotpass@db:5432/chatbotdb_test"
    SECRET_KEY: str = "secret-key"
    # Add more config variables as needed

    class Config:
        env_file = ".env"

settings = Settings()
