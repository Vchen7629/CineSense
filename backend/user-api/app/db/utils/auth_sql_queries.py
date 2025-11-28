from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.sessions import Session
import uuid
from datetime import datetime, timedelta, timezone

async def check_valid_session_token(db: AsyncSession, token: str):
    """Check db to see if the session exists, returns none if doesnt exist """
    query = select(Session).where(Session.session_token == token)
    result = await db.execute(query)
    session_record = result.scalar_one_or_none()

    # check if session exists and hasn't expired
    if session_record and session_record.expire_at > datetime.now(timezone.utc):
        return session_record
    return None

async def create_session(user_id: int, db: AsyncSession) -> str:
    token = str(uuid.uuid4())
    expire_time = datetime.now(timezone.utc) + timedelta(hours=1)

    # Check if user already has a session
    query = select(Session).where(Session.user_id == user_id)
    result = await db.execute(query)
    existing_session = result.scalar_one_or_none()

    if existing_session:
        # Update existing session with new token and expiry
        existing_session.session_token = token
        existing_session.expire_at = expire_time
        await db.flush()
    else:
        # Create new session
        session = Session(session_token=token, user_id=user_id, expire_at=expire_time)
        db.add(session)
        await db.flush()

    return token