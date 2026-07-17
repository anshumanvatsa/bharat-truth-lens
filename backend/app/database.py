from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

from .config import get_settings

settings = get_settings()

_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.mongo_uri,
            serverSelectionTimeoutMS=5000,  # 5s timeout instead of hanging
            connectTimeoutMS=10000,
        )
    return _client


def get_database() -> AsyncIOMotorDatabase:
    client = get_client()
    # Always use "civicpulse" — Atlas URI may not include DB name
    return client["civicpulse"]
