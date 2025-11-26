# Entry Point
from fastapi import FastAPI
from sqlalchemy import inspect

from .routes import status, user
from .db.dbConn import engine

from .db.base import Base
from . import models


app = FastAPI()

# Including routes from routes folder.
app.include_router(status.router, prefix="", tags=["status"])
app.include_router(user.router)

Base.metadata.create_all(bind=engine)


# printing out tables
with engine.connect() as conn:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("tables in DB:", tables)

    