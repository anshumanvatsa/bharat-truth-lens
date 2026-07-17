import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    app_name: str = "Pulse of India API"

    # MongoDB — accepts both MONGO_URI and MONGODB_URL env var names
    mongo_uri: str = (
        os.getenv("MONGO_URI")
        or os.getenv("MONGODB_URL")
        or "mongodb://localhost:27017/civicpulse"
    )

    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION_PLEASE")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # API keys
    tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
    groq_api_key: str | None   = os.getenv("GROQ_API_KEY")

    # CORS
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "*")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
