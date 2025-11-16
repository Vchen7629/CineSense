from sqlalchemy import text
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from typing import List
import numpy as np

async def get_user_genres(session, user_id: str):
    query = text("""
        SELECT user_id, top_3_genres, genre_embedding
        FROM user_top3_genres
        WHERE user_id = :user_id
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
async def new_user_genre_embedding(session, user_id: str, genre_embedding):
    query = text("""
        INSERT INTO user_genre_embeddings (user_id, genre_embedding, last_updated)
        VALUES (:user_id, :genre_embedding, NOW())
    """)
    
    try:
        await session.execute(
            query,
            {
                "user_id": str(user_id),
                "genre_embedding": genre_embedding
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
        FROM user_ratings;
    """)

    result = await session.execute(query)

    num_users = result.scalar() # get amount of users in int

    return num_users

# fetch the embeddings for specified user
async def get_user_embeddings(session, user_id: str):
    query = text("""
        SELECT embedding 
        FROM user_embeddings
        WHERE user_id = :user_id
    """)

    result = await session.execute(query, {"user_id": user_id})
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="embedding for user_id not found")
    
    return row.embedding

# find k-most similar users to provided embedding using pgvector hnsw index
async def find_similar_users(session, user_id: str, embedding: np.ndarray, similar_user_count: int = 50):
    query = text("""
        SELECT user_id, 1 - (embedding <=> :embedding) AS similarity
        FROM user_embeddings
        WHERE user_id != :user_id
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """)

    result = await session.execute(
        query,
        {   
            "embedding": embedding,
            "user_id": user_id,
            "limit": similar_user_count
        }
    )

    return result.fetchall()

# get candidate movies from similar users ranked by frequency counts
# returns list of movie_id, frequency_count
async def get_candidate_movies_from_similar_users(
    session,
    similar_user_ids: List[str],
    exclude_movie_ids: List[str],
    limit: int = 300
):
    # Convert lists to PostgreSQL array format for the query
    query = text("""
        SELECT movie_id, COUNT(*) as frequency
        FROM user_ratings
        WHERE user_id = ANY(:similar_user_ids)
        AND movie_id != ALL(:exclude_movie_ids)
        GROUP BY movie_id
        ORDER BY frequency DESC
        LIMIT :limit
    """)

    result = await session.execute(
        query,
        {
            "similar_user_ids": similar_user_ids,
            "exclude_movie_ids": exclude_movie_ids if exclude_movie_ids else [''],
            "limit": limit
        }
    )

    return result.fetchall()

async def get_user_rated_movie_ids(session, user_id: str):
    query = text("""
        SELECT movie_id
        FROM user_ratings
        WHERE user_id = :user_id
    """)

    result = await session.execute(query, {"user_id": user_id})
    rows = result.fetchall()

    return rows