from sqlalchemy import text
from typing import List
import numpy as np
from sqlalchemy.exc import IntegrityError
from asyncpg.exceptions import ForeignKeyViolationError
from fastapi import HTTPException

# sql function that inserts movie metadata and does nothing if it already exists
async def add_movie_metadata(
    session,
    movie_id: str, 
    movie_name: str = None, 
    genres: List[str] = None, 
    release_date: str = None, 
    summary: str = None, 
    actors: List[str] = None,
    director: List[str] = None,
    poster_path: str = None
):
    query = text("""
        INSERT INTO movie_metadata (
            movie_id, movie_name, genres, release_date, summary, actors, director, poster_path
        )
        VALUES (
            :movie_id, :movie_name, :genres, :release_date, :summary, :actors, :director, :poster_path
        )
        ON CONFLICT (movie_id) DO NOTHING
    """)

    if movie_name is not None:
        await session.execute(
            query,
            {
                "movie_id": str(movie_id),
                "movie_name": movie_name,
                "genres": genres,
                "release_date": release_date,
                "summary": summary,
                "actors": actors,
                "director": director,
                "poster_path": poster_path
            }
        )

        result = await session.execute(
            text("SELECT * FROM movie_metadata WHERE movie_name=:movie_name"), 
            {"movie_name": movie_name}
        )
        row = result.first()

        print(row)

# sql function to insert a embedding for a new movie, doesnt insert if exists
async def add_new_movie_embedding(session, movie_id: str, movie_embedding: List[np.ndarray]):

    query = text("""
        INSERT INTO movie_embedding_personalized (movie_id, embedding)
        VALUES (:movie_id, :embedding)
        ON CONFLICT (movie_id) DO NOTHING
    """)
    
    await session.execute(
        query,
        {
            "movie_id": str(movie_id),
            "embedding": str(movie_embedding)
        }
    )

async def add_new_movie_rating(session, user_id: str, movie_id: str, rating: int):
    query = text("""
        INSERT INTO user_ratings (user_id, movie_id, user_rating, added_at, updated_at)
        VALUES (:user_id, :movie_id, :user_rating, NOW(), NOW())
        ON CONFLICT (user_id, movie_id)
        DO UPDATE SET
            user_rating = EXCLUDED.user_rating,
            updated_at = NOW()
        RETURNING added_at = updated_at AS is_new   
    """)    

    try:
        result = await session.execute(
            query,
            {
                "user_id": user_id,
                "movie_id": movie_id,
                "user_rating": rating
            }
        )

        # trigger db flush to catch errors early
        await session.flush()
        row = result.first()
        is_new_rating = row.is_new if row else None 
        return is_new_rating
    except IntegrityError as e:
        error_message = str(e)
        # Check if it's a foreign key violation
        if "foreign key constraint" in error_message:
            if "user_ratings_user_id_fkey" in error_message or "user_login" in error_message:
                raise HTTPException(status_code=404, detail="User does not exist")
            elif "user_ratings_movie_id_fkey" in error_message or "movie_metadata" in error_message:
                raise HTTPException(status_code=404, detail="Movie does not exist")
            else:
                raise HTTPException(status_code=400, detail="Foreign key violation")
        else:
            raise HTTPException(status_code=400, detail="Database integrity error")


# fetches the movie_embeddings for the user
async def get_movie_embeddings(session, user_id: str):
    query = text("""
        SELECT e.embedding
        FROM user_ratings r
        JOIN movie_embedding_personalized e ON r.movie_id = e.movie_id
        WHERE r.user_id = :user_id
        ORDER BY r.updated_at DESC
    """)

    result = await session.execute(query, {"user_id": user_id})
    rows = result.fetchall()

    return rows

async def get_movie_embeddings_by_movie_ids(
    session, 
    movie_ids: List[str]
) -> List[tuple[str, np.ndarray]]:
    query = text("""
        SELECT movie_id, embedding
        FROM movie_embedding_personalized
        WHERE movie_id = ANY(:movie_id)
        ORDER BY array_position(:movie_ids::text[], movie_id)
    """)

    result = await session.execute(query, {"movie_id": movie_ids})
    rows = result.fetchall()

    return rows

async def get_movies_metadata_by_movie_ids(
    session, movie_ids: List[str]
):
    query = text("""
        SELECT movie_metadata (
            movie_id, movie_name, genres, release_date, summary, actors, director, poster_path
        )
        FROM movie_metadata
        WHERE movie_id = ANY(:movie_ids)
        ORDER BY array_position(:movie_ids::text[], movie_id)
    """)

    result = await session.execute(query, {"movie_ids": movie_ids})
    rows = result.fetchall()
    recommendations = [
        {
            "movie_id": row.movie_id,
            "title": row.movie_name,
            "genres": row.genres,
            "release_date": row.release_date,
            "summary": row.summary,
            "actors": row.actors,
            "director": row.director,
            "poster_path": row.poster_path
        }
        for row in rows
    ]

    return recommendations

# helper function for fetching cold start movies from db when users initially signs up,
# we only have the user's top 3 selected genres as signal for recommendations
async def get_cold_start_recommendations(session, user_embedding, top3_genre):

    # 80/20 split so that 80% of the movies returned initially match the user's
    # initial selected movies and 20% of movies arent so recommendations can recommend
    # new movies without being locked to those 3 genres
    query = text("""
        WITH genre_matched AS (
            SELECT
                m.movie_id,
                m.movie_name,
                m.genres,
                m.release_date, 
                m.summary, 
                m.actors, 
                m.director, 
                m.poster_path,
                (e.embedding <=> CAST(:user_embedding AS vector)) as distance
            FROM movie_metadata m
            JOIN movie_embedding_coldstart e ON m.movie_id = e.movie_id
            WHERE m.genres && CAST(:user_genres AS text[])
            ORDER BY distance
            LIMIT 8
        ),
        random_other AS (
            SELECT
                m.movie_id,
                m.movie_name,
                m.genres,
                m.release_date, 
                m.summary, 
                m.actors, 
                m.director, 
                m.poster_path,
                999 as distance
            FROM movie_metadata m
            WHERE NOT (m.genres && CAST(:user_genres AS text[]))
            ORDER BY RANDOM()
            LIMIT 2
        )
        SELECT movie_id, movie_name, genres, release_date, summary, actors, director, poster_path, distance
        FROM genre_matched
        UNION ALL
        SELECT movie_id, movie_name, genres, release_date, summary, actors, director, poster_path, distance
        FROM random_other
        ORDER BY distance;
    """)

    result = await session.execute(
        query,
        {
            "user_embedding": str(user_embedding),
            "user_genres": top3_genre
        }
    )

    movies = result.fetchall()

    recommendations = [
        {
            "movie_id": row.movie_id,
            "title": row.movie_name,
            "genres": row.genres,
            "release_date": row.release_date,
            "summary": row.summary,
            "actors": row.actors,
            "director": row.director,
            "poster_path": row.poster_path
        }
        for row in movies
    ]

    return recommendations