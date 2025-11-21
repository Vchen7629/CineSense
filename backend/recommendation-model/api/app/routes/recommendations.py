from fastapi import APIRouter, Depends, Request
from db.config.conn import get_session
from db.utils.movies import get_movies_metadata_by_movie_ids, get_cold_start_recommendations
from db.utils.user import (
    get_user_genres, 
    get_user_with_ratings_count, 
    get_similar_users_and_user_metadata,
    get_user_rated_movie_ids,
)
from model.utils.reranker_model import Reranker
from sqlalchemy.ext.asyncio import AsyncSession
from utils.dependencies import get_reranking_model

router = APIRouter(prefix="/recommendations")

@router.get("/get/{user_id}")
async def get_recommendations(
    user_id: str, 
    session: AsyncSession = Depends(get_session), 
    rerank_model: Reranker = Depends(get_reranking_model)
):
    num_users = await get_user_with_ratings_count(session)

    # fallback to cold start recommendations if not enough users
    if num_users < 50:
        top3_genre, genre_embedding = await get_user_genres(session, user_id)
        recommendations = await get_cold_start_recommendations(session, genre_embedding, top3_genre)
        print("less than 50 users: cold start recos")
        return recommendations
    
    rated_movie_ids = await get_user_rated_movie_ids(session, user_id)

    # # fallback to cold start recommendations if less than 10 rated movies
    if len(rated_movie_ids) < 10:
        top3_genre, genre_embedding = await get_user_genres(session, user_id)
        recommendations = await get_cold_start_recommendations(session, genre_embedding, top3_genre)
        print("less than 50 users: cold start recos")
        return recommendations

    # get user metadata for current user and similar users userIds
    user_metadata, similar_users = await get_similar_users_and_user_metadata(session, user_id, similar_user_count=50)

    # get movie_ids of similar users 
    excluded_movies_ids = [row[0] for row in rated_movie_ids]

    # fetch our candidate movies from collaborative filtering, default 300 movies
    candidate_movies = await get_movies_metadata_by_movie_ids(session, similar_users, excluded_movies_ids)

    await session.commit()

    # use lightgbm reranking model to reduce 300 candidate movies down to 10 best movies for the specific user
    collaborative_recommendations = rerank_model.rerank_movies(user_metadata, candidate_movies)

    return collaborative_recommendations