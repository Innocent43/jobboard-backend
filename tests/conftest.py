import pytest
from fastapi.testclient import TestClient
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker,Session
from httpx import AsyncClient,ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.pool import NullPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.core.config import settings
from app.core.limiter import limiter


TEST_DATABASE_URL = settings.test_database_url.replace("postgresql://","postgresql+asyncpg://")

@pytest.fixture(scope="function")

async def db_session() -> AsyncSession:
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    TestingSessionLocal = async_sessionmaker(bind=engine,expire_on_commit=False)


    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncClient:
    async def override_get_db():
            yield db_session

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
         yield test_client

    app.dependency_overrides.clear()
   