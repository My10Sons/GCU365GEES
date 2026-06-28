"""
Repository Traceability:
- Source Documents: DI-SPRINT-00 (Database Setup), DI-0014 (tenant isolation enforced
  in collection-level access patterns), DECISION-004 (MongoDB substitution for PostgreSQL)
- Purpose: MongoDB connection lifecycle.
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.environ["MONGO_URL"], serverSelectionTimeoutMS=5000)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_client()[os.environ["DB_NAME"]]
    return _db


async def ping() -> bool:
    try:
        await get_client().admin.command("ping")
        return True
    except Exception:
        return False


async def close() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None
