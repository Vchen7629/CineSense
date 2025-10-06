# Entry Point
from fastapi import FastAPI
from app.routes import status

app = FastAPI()

# Including routes from routes folder
app.include_router(status.router, prefix="", tags=["status"])
