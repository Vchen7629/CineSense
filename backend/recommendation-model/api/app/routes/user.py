from fastapi import APIRouter, Request, Depends
from model.utils.cold_start_user_tower import ColdStartUserTower
from db.utils.user import new_user_genre_embedding, test
from db.config.conn import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from utils.dependencies import get_cold_start_user_tower
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/user", tags=["user"])

class NewUserRequest(BaseModel):
    genres: List[str]

# we need to create an embedding using the user tower for the
# selected top 3 genres for cold start recommendations
@router.post("/genre_embedding/{userId}")
async def new_user(
    userId: str,
    body: NewUserRequest,
    session: AsyncSession = Depends(get_session),
    user_tower: ColdStartUserTower = Depends(get_cold_start_user_tower)
):
    genres = body.genres
    user_embedding = user_tower.embedding(genres)

    await new_user_genre_embedding(session, userId, user_embedding)

    return {"message": f"successfully added genre embeddings for user: {userId}"}

# we need to create an embedding using the user tower for the
# selected top 3 genres for cold start recommendations
@router.get("/create/{userId}")
async def new_user(
    userId: str,
    session: AsyncSession = Depends(get_session),
):
    result = await test(session, userId)

    return result