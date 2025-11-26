# Define how data is stored in the Sessions Table, session_id, user_id, expiry_time, etc

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime 
from sqlalchemy.sql import func
from ..db.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime(timezone = True), server_default=func.now())