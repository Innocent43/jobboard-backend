# from sqlalchemy import create_engine
# from sqlalchemy.engine import Engine
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncEngine,create_async_engine

ASYN_DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")

connect_args={"ssl": "require"} if "render.com" in ASYN_DATABASE_URL or "dpg-" in ASYN_DATABASE_URL else {}

engine: AsyncEngine = create_async_engine(ASYN_DATABASE_URL, connect_args=connect_args)
