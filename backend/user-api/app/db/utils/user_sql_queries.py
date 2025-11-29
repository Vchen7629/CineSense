from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from models.sessions import Session
from datetime import datetime, timezone

async def get_user_by_email(session: AsyncSession, email: str):
    """Check if a user exists by email, returns none if doesnt exist"""
    query = select(User).where(User.email == email)
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def get_user_by_session_token(session: AsyncSession, token: str):
    """Returns userdata using the session token from the database"""
    query = (
        select(User)
        .join(Session, User.user_id == Session.user_id)
        .where(Session.session_token == token)
        .where(Session.expire_at > datetime.now(timezone.utc))
    )

    result = await session.execute(query)

    return result.scalar_one_or_none()