# Entry Point
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import inspect
import uvicorn
from db.config.conn import engine
from routes import base, auth
from utils.env_config import settings
from middleware.cors import add_cors
import logging

logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# lifespan for managing database connection/cleanup
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CineSense User Auth API")
    # Print out tables
    async with engine.connect() as conn:
        def get_tables(sync_conn):
            inspector = inspect(sync_conn)
            return inspector.get_table_names()

        tables = await conn.run_sync(get_tables)
        logger.info(f"Tables in DB: {tables}")
    logger.info("Database connection established")

    yield

    logger.info("Shutting down...")
    await engine.dispose()
    logger.info("Shutdown complete!")

app = FastAPI(lifespan=lifespan)

# middleware
add_cors(app)

# Including routes from routes folder.
app.include_router(base.router, prefix="", tags=["status"])
app.include_router(auth.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    