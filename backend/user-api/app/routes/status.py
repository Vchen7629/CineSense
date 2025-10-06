# Sample Routes for Health Checking
from fastapi import APIRouter

router = APIRouter()

# Initial Route
@router.get("/")
async def health():
    return {"message": "hello world"}


# Health endpoint used to check system health
@router.get("/apihealth")
async def health():
    return {"status": "ok"}
