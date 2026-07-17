import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseSettings):
    app_name: str = "CivicPulse AI Backend"
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/civicpulse")
    jwt_secret_key: str = os.getenv("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")

    frontend_origin: AnyUrl | str | None = os.getenv("FRONTEND_ORIGIN", "*")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()

