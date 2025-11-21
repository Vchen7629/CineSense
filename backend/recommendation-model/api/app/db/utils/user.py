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

async def test(session, user_id: str):
    query = text("""
        INSERT INTO user_login (user_id, username, email, password, created_at)
        VALUES (:user_id, :username, :email, :password, :created_at)
    """)
    try:
        await session.execute(
            query,
            {
                "user_id": str(user_id),
                "username": f"test_{user_id}",
                "email": f"test{user_id}@example.com",
                "password": "test123",
                "created_at": datetime(2025, 11, 12, 14, 30, 45)
            }
        )
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail="User already exists") from e

    result = await session.execute(text("SELECT * FROM user_login"))
    
    rows = result.fetchall()
    rows_as_dicts = [dict(row._mapping) for row in rows]

    return rows_as_dicts

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
# and also their user embedding
async def get_user_embedding_and_similar_users(session, user_id: str, similar_user_count: int = 50):
    query = text("""
        WITH current_user AS (
            SELECT user_id, embedding
            FROM user_embeddings
            WHERE user_id = :user_id
        )
        SELECT 
            ue.user_id, 
            1 - (ue.embedding <=> :cu.embedding) AS similarity,
            cu.embedding as user_embedding
        FROM user_embeddings ue
        CROSS JOIN current_user cu
        WHERE ue user_id != :user_id
        ORDER BY ue.embedding <=> :cu.embedding
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
    
    user_embedding = rows[0].user_embedding

    return user_embedding, rows

async def get_user_rated_movie_ids(session, user_id: str):
    query = text("""
        SELECT movie_id
        FROM user_watchlist
        WHERE user_id = :user_id
    """)

    result = await session.execute(query, {"user_id": user_id})
    rows = result.fetchall()

    return rows