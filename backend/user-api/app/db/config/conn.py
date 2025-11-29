# Code for connecting to the PostgreSQL Database
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from typing import AsyncGenerator
from utils.env_config import settings

DATABASE_URL = settings.database_url

#be able to talk to the database
engine: AsyncEngine = create_async_engine(url=DATABASE_URL, echo=settings.debug, pool_pre_ping=True)

# session factory
async_session = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


# creates a short lived session from the sessionmaker factory
# used per request
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()