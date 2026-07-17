from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

from .config import get_settings


settings = get_settings()

_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_uri)
    return _client


def get_database() -> AsyncIOMotorDatabase:
    client = get_client()
    # If `mongo_uri` includes DB name, use it, otherwise default to "civicpulse"
    db_name = client.get_default_database().name if client.get_default_database() is not None else "civicpulse"
    return client[db_name]

