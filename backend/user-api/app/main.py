# Entry Point
from fastapi import FastAPI
from routes import status
from db.dbConn import engine
from sqlalchemy import inspect

app = FastAPI()

# Including routes from routes folder.
app.include_router(status.router, prefix="", tags=["status"])

# printing out tables
with engine.connect() as conn:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(tables)

