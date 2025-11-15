from fastapi import APIRouter, Depends, Request
from db.config.conn import get_session
from model.utils.cold_start_user_tower import ColdStartUserTower
from db.utils.movies import get_movies_metadata_by_movie_ids, get_cold_start_recommendations
from db.utils.user import (
    get_user_genres, 
    get_user_with_ratings_count, 
    get_user_embeddings, 
    find_similar_users,
    get_candidate_movies_from_similar_users,
    get_user_rated_movie_ids,
)
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

router = APIRouter(prefix="/recommendations")

@router.get("/get/{user_id}")
async def get_recommendations(user_id: str, session: AsyncSession = Depends(get_session)):
    num_users = await get_user_with_ratings_count(session)

    # fallback to cold start recommendations if not enough users
    if num_users < 50:
        top3_genre, genre_embedding = await get_user_genres(session, user_id)
        recommendations = await get_cold_start_recommendations(session, genre_embedding, top3_genre)
        print("less than 50 users: cold start recos")
        return recommendations

    rated_movie_ids = await get_user_rated_movie_ids(session, user_id)

    # if less than 10 ratings fallback to cold start embeddings
    if len(rated_movie_ids) < 10:
        top3_genre, genre_embedding = await get_user_genres(session, user_id)
        recommendations = await get_cold_start_recommendations(session, genre_embedding, top3_genre)
        print("less than 10 ratings: cold start recos")
        return recommendations
    
    # get user embedding for current user
    user_embedding = await get_user_embeddings(session, user_id)    

    # get user embeddings of similar users
    similar_users = await find_similar_users(session, user_id, user_embedding, similar_user_count=50)

    # get movie_ids of similar users 
    excluded_movies_ids = [row[0] for row in rated_movie_ids]
    movie_ids = await get_candidate_movies_from_similar_users(session, similar_users, excluded_movies_ids)

    relevant_movies = get_movies_metadata_by_movie_ids(session, movie_ids)

    await session.commit()

    return relevant_movies