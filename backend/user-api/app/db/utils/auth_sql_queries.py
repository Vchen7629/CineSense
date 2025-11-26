from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.sessions import Session
import uuid
from datetime import datetime, timedelta, timezone

async def check_valid_session_token(session: AsyncSession, token: str):
    """Check db to see if the session exists, returns none if doesnt exist """
    query = select(Session).where(Session.session_token == token)
    result = await session.execute(query)
    session = result.scalar_one_or_none()

async def create_session(user_id: int, db: AsyncSession) -> str:
    token = str(uuid.uuid4())

    expire_time = datetime.now(timezone.utc) + timedelta(hours=1)
    session = Session(session_token=token, user_id=user_id, expire_at=expire_time)
    db.add(session)
    await db.flush()

    return token