# Define how data is stored in the Users Table, user_id, username, password, etc

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from db.config.base import Base

class User(Base): 
    __tablename__ = "user_login"

    user_id = Column(Text, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default='NOW()')
