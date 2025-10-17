from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from .models import meta

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncConnection

engine = create_async_engine(settings.DATABASE_URL)
db_metadata = meta


async def get_db_connection() -> AsyncConnection:
    conn = await engine.connect()
    try:
        yield conn
    finally:
        await conn.close()
