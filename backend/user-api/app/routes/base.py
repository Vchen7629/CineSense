# Sample Routes for Health Checking
from fastapi import APIRouter
from typing import Dict

router = APIRouter()


# Initial Route
@router.get("/")
async def home() -> Dict[str, str]:
    return {"message": "hello world"}


# Health endpoint used to check system health
@router.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}
