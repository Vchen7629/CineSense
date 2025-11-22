from sqlalchemy import text
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List
import numpy as np

async def get_user_genres(session, user_id: str):
    query = text("""
        SELECT e.user_id, r.top_3_genres, e.genre_embedding
        FROM user_genre_embeddings e
        JOIN user_rating_stats r ON e.user_id = r.user_id
        WHERE e.user_id = :user_id
    """)

    result = await session.execute(
        query,
        {"user_id": str(user_id)}
    )

    genre_info = result.fetchone()

    if not genre_info:
        raise HTTPException(status_code=404, detail="User not found")
    
    top_3_genres = genre_info.top_3_genres
    genre_embedding = genre_info.genre_embedding

    return top_3_genres, genre_embedding

# create a new user embedding using the 3 genres selected during signup
async def new_user_genre_embedding(session, user_id: str, genre_embedding: np.ndarray, top3_genres: List[str]):
    query = text("""
        WITH insert1 AS (
            INSERT INTO user_genre_embeddings (user_id, genre_embedding, last_updated)
            VALUES (:user_id, :genre_embedding, NOW())
            RETURNING user_id
        )
        INSERT INTO user_rating_stats (user_id, top_3_genres)
        SELECT user_id, :top_3_genres
        FROM insert1
    """)
    
    try:
        await session.execute(
            query,
            {
                "user_id": str(user_id),
                "genre_embedding": genre_embedding,
                "top_3_genres": top3_genres,
            }
        )
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        error_message = str(e).lower()
        # Check if it's a foreign key violation
        if "foreign key constraint" in error_message:
            if "user_genre_embeddings_user_id_fkey" in error_message or "user_login" in error_message:
                raise HTTPException(status_code=404, detail="User does not exist")
            else:
                raise HTTPException(status_code=400, detail="Foreign key violation")
        # Check if it's a duplicate key violation
        elif "unique constraint" in error_message or "duplicate key" in error_message:
            raise HTTPException(status_code=409, detail="Genre embedding already exists for this user")
        else:
            raise HTTPException(status_code=400, detail="Database integrity error")

# regenerates the user embedding containing their rated movies by averaging
# the movie embeddings
async def regenerate_user_movie_embedding(session, user_id: str, user_emb: np.ndarray):
    # insert/update user embedding
    upsert_query = text("""
        INSERT into user_embeddings (user_id, embedding, last_updated)
        VALUES (:user_id, :embedding, NOW())
        ON CONFLICT (user_id)
        DO UPDATE SET
            embedding = EXCLUDED.embedding,
            last_updated = NOW()
    """)

    await session.execute(
        upsert_query,
        {
            "user_id": user_id,
            "embedding": str(user_emb.tolist())
        }
    )
    
# fetch the amount of users that have rated at least one movie in the database
async def get_user_with_ratings_count(session):
    query = text("""
        SELECT COUNT(DISTINCT user_id)
        FROM user_watchlist;
    """)

    result = await session.execute(query)

    num_users = result.scalar() # get amount of users in int

    return num_users


# find k-most similar users to current user embedding using pgvector hnsw index
# and also their user embedding and rating metadata needed for the lightgbm reranker
async def get_similar_users_and_user_metadata(session, user_id: str, similar_user_count: int = 50):
    query = text("""
        WITH target_user AS (
            SELECT
                ue.user_id,
                ue.embedding,
                urs.avg_rating,
                urs.rating_count_log,
                urs.top_3_genres,
                urs.top_50_actors,
                urs.top_10_directors
            FROM user_embeddings ue
            JOIN user_rating_stats urs ON ue.user_id = urs.user_id
            WHERE ue.user_id = :user_id
        )
        SELECT
            ue.user_id,
            1 - (ue.embedding <=> tu.embedding) AS similarity,
            tu.embedding as user_embedding,
            tu.avg_rating as user_avg_rating,
            tu.rating_count_log as user_rating_log,
            tu.top_3_genres,
            tu.top_50_actors,
            tu.top_10_directors
        FROM user_embeddings ue
        CROSS JOIN target_user tu
        WHERE ue.user_id != :user_id
        ORDER BY ue.embedding <=> tu.embedding
        LIMIT :limit
    """)

    result = await session.execute(
        query,
        {   
            "user_id": user_id,
            "limit": similar_user_count
        }
    )

    rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail="User embedding not found")
    
    # extract all user metadata from first row
    user_embedding = rows[0].user_embedding
    user_avg_rating = rows[0].user_avg_rating
    user_rating_log = rows[0].user_rating_log
    top_3_genres = rows[0].top_3_genres
    top_50_actors = rows[0].top_50_actors
    top_10_directors = rows[0].top_10_directors

    return {
        'embedding': user_embedding,
        'avg_rating': user_avg_rating,
        'rating_log': user_rating_log,
        'top_3_genres': top_3_genres,
        'top_50_actors': top_50_actors,
        'top_10_directors': top_10_directors
    }, rows

async def get_user_rated_movie_ids(session, user_id: str):
    query = text("""
        SELECT movie_id
        FROM user_watchlist
        WHERE user_id = :user_id
    """)

    result = await session.execute(query, {"user_id": user_id})
    rows = result.fetchall()

    return rows

async def update_user_ratings_stats(session, user_id: str):
    query = text("""
        WITH user_movies AS (
            SELECT 
                m.genres,
                m.actors,
                m.director
            FROM user_watchlist uw
            JOIN movie_metadata m on uw.movie_id = m.movie_id
            WHERE uw.user_id = :user_id
        ),
        user_stats AS (
            SELECT
                COUNT(*) as count,
                CAST(AVG(user_rating) AS REAL) as avg
            FROM user_watchlist
            WHERE user_id = :user_id
        ),
        top_genres AS (
            SELECT genre
            FROM (
                SELECT UNNEST(genres) as genre
                FROM user_movies
            ) g
            GROUP BY genre
            ORDER BY COUNT(*) DESC
            LIMIT 3
        ),
        top_actors AS (
            SELECT actor
            FROM (
                SELECT UNNEST(actors) as actor
                FROM user_movies
            ) a
            GROUP BY actor
            ORDER BY COUNT(*) DESC
            LIMIT 50
        ),
        top_directors AS (
            SELECT director
            FROM (
                SELECT UNNEST(director) as director
                FROM user_movies
            ) d
            GROUP BY director
            ORDER BY COUNT(*) DESC
            LIMIT 10
        )
        INSERT INTO user_rating_stats (
            user_id,
            avg_rating,
            rating_count,
            rating_count_log,
            top_3_genres,
            top_50_actors,
            top_10_directors,
            last_updated
        )
        SELECT
            :user_id,
            COALESCE((SELECT avg FROM user_stats), 0.0),
            COALESCE((SELECT count FROM user_stats), 0),
            LN(COALESCE((SELECT count FROM user_stats), 0) + 1),
            COALESCE((SELECT ARRAY_AGG(genre) FROM top_genres), ARRAY[]::TEXT[]),
            COALESCE((SELECT ARRAY_AGG(actor) FROM top_actors), ARRAY[]::TEXT[]),
            COALESCE((SELECT ARRAY_AGG(director) FROM top_directors), ARRAY[]::TEXT[]),
            NOW()
        ON CONFLICT (user_id)
        DO UPDATE SET
            avg_rating = EXCLUDED.avg_rating,
            rating_count = EXCLUDED.rating_count,
            rating_count_log = EXCLUDED.rating_count_log,
            top_3_genres = EXCLUDED.top_3_genres,
            top_50_actors = EXCLUDED.top_50_actors,
            top_10_directors = EXCLUDED.top_10_directors,
            last_updated = EXCLUDED.last_updated
        RETURNING *
    """)

    result = await session.execute(query, {"user_id": user_id})

    if not result:
        raise HTTPException(status_code=500, detail="error updating user rating stats")