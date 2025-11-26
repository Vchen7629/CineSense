# Define how data is stored in the Users Table, user_id, username, password, etc

from sqlalchemy import Column, Integer, String
from ..db.base import Base

class User(Base): 
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)