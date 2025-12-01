from fastapi import APIRouter, Depends
from db.config.conn import get_session
from db.utils.movies_sql_queries import (
    get_movies_metadata_by_movie_ids, 
    get_cold_start_recommendations,
    get_movie_embeddings,
)
from db.utils.user_sql_queries import (
    get_user_genres, 
    get_user_with_ratings_count, 
    get_similar_users_and_user_metadata,
    get_user_rated_movie_ids,
    check_user_rating_stats_stale,
    update_user_ratings_stats,
    set_user_rating_stats_fresh,
    regenerate_user_movie_embedding
)
from model.utils.reranker_model import Reranker
from sqlalchemy.ext.asyncio import AsyncSession
from utils.dependencies import get_reranking_model
import numpy as np

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
        recommendations = await get_cold_start_recommendations(session, user_id, genre_embedding, top3_genre)
        print("less than 50 users: cold start recos")
        return recommendations
    
    rated_movie_ids = await get_user_rated_movie_ids(session, user_id)

    # # fallback to cold start recommendations if less than 10 rated movies
    if len(rated_movie_ids) < 10:
        top3_genre, genre_embedding = await get_user_genres(session, user_id)
        recommendations = await get_cold_start_recommendations(session, user_id, genre_embedding, top3_genre)
        print("less than 50 users: cold start recos")
        return recommendations
    
    # check if the user rating stats table is stale for the user, if so we need to 
    # recalculate the user embeddings
    row = await check_user_rating_stats_stale(session, user_id)

    if row and row.is_stale:
        movie_embeddings_rows = await get_movie_embeddings(session, user_id)

        # parse pgvector string format to numpy arrays
        movie_embeddings = []
        for row in movie_embeddings_rows:
            embedding_str = row[0].strip('[]')
            embedding = np.fromstring(embedding_str, sep=',', dtype=np.float32)
            movie_embeddings.append(embedding)

        movie_embeddings = np.array(movie_embeddings, dtype=np.float32)

        # average and normalize
        user_emb = movie_embeddings.mean(axis=0) # [512]
        user_emb = user_emb / np.linalg.norm(user_emb)

        await regenerate_user_movie_embedding(session, user_id, user_emb)
        await update_user_ratings_stats(session, user_id)

        await set_user_rating_stats_fresh(session, user_id)

    # get user metadata for current user and similar users userIds
    user_metadata, similar_users = await get_similar_users_and_user_metadata(session, user_id, similar_user_count=50)

    # get movie_ids of similar users
    excluded_movies_ids = [row[0] for row in rated_movie_ids]

    # extract just the user_ids from similar_users rows
    similar_user_ids = [row.user_id for row in similar_users]

    # fetch our candidate movies from collaborative filtering, default 300 movies
    candidate_movies = await get_movies_metadata_by_movie_ids(session, similar_user_ids, excluded_movies_ids)

    # use lightgbm reranking model to reduce 300 candidate movies down to 10 best movies for the specific user
    collaborative_recommendations = rerank_model.rerank_movies(user_metadata, candidate_movies)

    return collaborative_recommendations