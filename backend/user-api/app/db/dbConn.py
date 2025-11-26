# Code for connecting to the PostgreSQL Database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .base import Base

#be able to talk to the database
engine = create_engine(
    "postgresql+psycopg://postgres:password@localhost:5432/example_db", 
    future = True,
)

#Session Factory -> gives us DB session per request
SessionLocal = sessionmaker(autocommit = False, autoflush= False, bind=engine)


def get_db() -> Session:

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()