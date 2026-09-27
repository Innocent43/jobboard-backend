from collections.abc import Generator
from sqlalchemy.orm import Session,sessionmaker
from app.database.engine import engine

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

# SessionLocal: sessionmaker[Session] = sessionmaker(bind=engine)

AsyncSessionLocal: async_sessionmaker[AsyncSession] =async_sessionmaker(bind=engine, expire_on_commit=False)

# def get_db()-> Generator[Session,None,None]:
#     db: Session = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


async def get_db() -> AsyncGenerator[AsyncSession,None]:
    async with AsyncSessionLocal() as session:
        yield session
