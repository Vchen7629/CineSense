# Code for connecting to the PostgreSQL Database
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from utils.config import settings

DATABASE_URL = settings.database_url

engine = create_async_engine(url=DATABASE_URL, echo=True)

# session factor
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# creates a short lived session from the sessionmaker factory
# used per request
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session