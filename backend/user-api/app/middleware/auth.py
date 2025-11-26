# middleware helper for using session cookie and
# fetching user_id from table for later authentication


import uuid
from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.config.conn import get_session
from models.sessions import Session as SessionModel
from models.users import User
from datetime import datetime, timedelta, timezone

SESSION_COOKIE_NAME = "session_token"


def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> User:
    
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise  HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )
    
    session = (
        db.query(SessionModel)
        .filter(SessionModel.session_token == token)
        .first()
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )
    
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User Not Found",
        )
    return user