# Entry Point
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import inspect
import uvicorn
from db.config.conn import engine, async_session
from sqlalchemy import text
from routes import status, user

# lifespan for managing database connection/cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session() as session:
          await session.execute(text("SELECT 1"))
    print("Database connection verified!")
    yield

    await engine.dispose()

app = FastAPI()

# Including routes from routes folder.
app.include_router(status.router, prefix="", tags=["status"])
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    