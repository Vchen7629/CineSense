# Entry Point
from fastapi import FastAPI
from sqlalchemy import inspect
import uvicorn

from routes import status, user
from db.dbConn import engine

from db.base import Base


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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    