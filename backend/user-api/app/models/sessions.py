# Define how data is stored in the Sessions Table, session_id, user_id, expiry_time, etc

from sqlalchemy import Column, ForeignKey, DateTime, Text
from db.config.base import Base

class Session(Base):
    __tablename__ = "sessions"

    user_id = Column(Text, ForeignKey("user_login.user_id", ondelete="CASCADE"), primary_key=True, unique=True, index=True)
    session_token = Column(Text, unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone = True), server_default='NOW()')
    expire_at = Column(DateTime(timezone=True), nullable=False)
