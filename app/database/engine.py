# from sqlalchemy import create_engine
# from sqlalchemy.engine import Engine
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncEngine,create_async_engine

ASYN_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

engine: AsyncEngine = create_async_engine(ASYN_DATABASE_URL)
