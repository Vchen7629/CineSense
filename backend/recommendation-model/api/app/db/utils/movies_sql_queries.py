from sqlalchemy import text
from typing import List
import numpy as np
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

# sql function that inserts movie metadata and does nothing if it already exists
async def add_movie_metadata(
    session,
    movie_id: str, 
    movie_name: str, 
    genres: List[str], 
    release_date: int, 
    summary: str, 
    actors: List[str],
    language: str,
    director: List[str],
    poster_path: str
):
    query = text("""
        INSERT INTO movie_metadata (
            movie_id, movie_name, genres, release_date, summary, actors, director, language, poster_path
        )
        VALUES (
            :movie_id, :movie_name, :genres, :release_date, :summary, :actors, :director, :language, :poster_path
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
                "language": language,
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
        INSERT INTO movie_embedding_personalized_prod (movie_id, embedding)
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

# sql function to add the new movie rating into user watchlist table 
async def add_new_movie_rating(session, user_id: str, movie_id: str, rating: float):
    query = text("""
        INSERT INTO user_watchlist (user_id, movie_id, user_rating, added_at, updated_at)
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

# update the movie rating stats table for most updated stats that reranker can use
async def update_movie_rating_stats(session, movie_id: str, tmdb_avg_rating: float, tmdb_vote_log: float, tmdb_popularity: float):
    query = text("""
        WITH movie_stats AS (
            SELECT
                COUNT(*) as count,
                CAST(AVG(user_rating) AS REAL) as avg
            FROM user_watchlist
            WHERE movie_id = :movie_id
            AND user_rating > 0
        )
        INSERT INTO movie_rating_stats (
            movie_id,
            avg_rating,
            rating_count,
            rating_count_log,
            tmdb_avg_rating,
            tmdb_vote_log,
            tmdb_popularity,
            last_updated
        )
        SELECT 
            :movie_id,
            movie_stats.avg,
            movie_stats.count,
            LN(movie_stats.count + 1),
            :tmdb_avg_rating,
            :tmdb_vote_log,
            :tmdb_popularity,
            NOW()
        FROM movie_stats
        ON CONFLICT (movie_id)
        DO UPDATE SET 
            avg_rating = EXCLUDED.avg_rating,
            rating_count = EXCLUDED.rating_count,
            rating_count_log = EXCLUDED.rating_count_log,
            tmdb_avg_rating = EXCLUDED.tmdb_avg_rating,
            tmdb_vote_log = EXCLUDED.tmdb_vote_log,
            tmdb_popularity = EXCLUDED.tmdb_popularity,
            last_updated = NOW()          
    """)

    result = await session.execute(query,
        {
            "movie_id": movie_id,
            "tmdb_avg_rating": tmdb_avg_rating,
            "tmdb_vote_log": tmdb_vote_log,
            "tmdb_popularity": tmdb_popularity
        }    
    )

    if not result:
        raise HTTPException(status_code=500, detail="failed to update movie rating to latest stats")

# fetches the movie_embeddings for the user
async def get_movie_embeddings(session, user_id: str):
    query = text("""
        SELECT e.embedding
        FROM user_watchlist r
        JOIN movie_embedding_personalized_prod e ON r.movie_id = e.movie_id
        WHERE r.user_id = :user_id
        AND r.user_rating > 0
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
        FROM movie_embedding_personalized_prod
        WHERE movie_id = ANY(:movie_id)
        ORDER BY array_position(:movie_ids::text[], movie_id)
    """)

    result = await session.execute(query, {"movie_id": movie_ids})
    rows = result.fetchall()

    return rows

# get movie metadata for all similar user ids found by most similar cosine sim
# and wasnt watched/rated by the current user
async def get_movies_metadata_by_movie_ids(
    session, 
    similar_user_ids: List[str],
    exclude_movie_ids: List[str],
    limit: int = 300
):
    query = text("""
        WITH candidate_movies AS (
            SELECT movie_id, COUNT(*) as frequency
            FROM user_watchlist
            WHERE user_id = ANY(:similar_user_ids)
            AND movie_id != ALL(:exclude_movie_ids)
            AND user_rating > 0
            GROUP BY movie_id
            ORDER BY frequency DESC
            LIMIT :limit
        )
        SELECT 
            m.*,
            mrs.*,
            emb.embedding as movie_embedding,
            c.frequency
        FROM candidate_movies c
        JOIN movie_metadata m ON c.movie_id = m.movie_id
        JOIN movie_rating_stats mrs on c.movie_id = mrs.movie_id
        JOIN movie_embedding_personalized_prod emb ON c.movie_id = emb.movie_id
        ORDER BY c.frequency DESC
    """)

    result = await session.execute(
        query, 
        {
            "similar_user_ids": similar_user_ids,
            "exclude_movie_ids": exclude_movie_ids if exclude_movie_ids else [''],
            "limit": limit
        }
    )

    rows = result.fetchall()
    recommendations = [
        {
            "movie_id": row.movie_id,
            "movie_emb": row.movie_embedding,
            "title": row.movie_name,
            "genres": row.genres,
            "release_date": row.release_date,
            "summary": row.summary,
            "actors": row.actors,
            "directors": row.director,
            "language": row.language,
            "poster_path": row.poster_path,
            "movie_rating_log": row.rating_count_log,
            "movie_avg_rating": row.avg_rating,
            "tmdb_vote_avg": row.tmdb_avg_rating,
            "tmdb_vote_log": row.tmdb_vote_log,
            "tmdb_popularity": row.tmdb_popularity
        }
        for row in rows
    ]

    return recommendations

# helper function for fetching cold start movies from db when users initially signs up,
# we only have the user's top 3 selected genres as signal for recommendations
async def get_cold_start_recommendations(session, user_id: str, user_embedding, top3_genre):

    # 80/20 split so that 80% of the movies returned initially match the user's
    # initial selected movies and 20% of movies arent so recommendations can recommend
    # new movies without being locked to those 3 genres
    query = text("""
        WITH excluded_movies AS (
            SELECT movie_id
            FROM user_watchlist
            WHERE user_id = :user_id
            AND user_rating > 0
            UNION
            SELECT movie_id
            FROM user_not_seen_movie
            WHERE user_id = :user_id
            AND (dismissed_until IS NULL OR dismissed_until > NOW())
        ),
        genre_matched AS (
            SELECT
                m.movie_id,
                m.movie_name,
                m.genres,
                m.release_date,
                m.summary,
                m.actors,
                m.director,
                m.language,
                m.poster_path,
                mrs.tmdb_avg_rating,
                mrs.tmdb_vote_log,
                mrs.tmdb_popularity,
                (e.embedding <=> CAST(:user_embedding AS vector)) as distance
            FROM movie_metadata m
            JOIN movie_embedding_coldstart_prod e ON m.movie_id = e.movie_id
            JOIN movie_rating_stats mrs ON m.movie_id = mrs.movie_id
            WHERE m.genres && CAST(:user_genres AS text[])
            AND m.movie_id NOT IN (SELECT movie_id FROM excluded_movies)
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
                m.language,
                m.poster_path,
                mrs.tmdb_avg_rating,
                mrs.tmdb_vote_log,
                mrs.tmdb_popularity,
                999 as distance
            FROM movie_metadata m
            JOIN movie_rating_stats mrs ON m.movie_id = mrs.movie_id
            WHERE NOT (m.genres && CAST(:user_genres AS text[]))
            AND m.movie_id NOT IN (SELECT movie_id FROM excluded_movies)
            ORDER BY RANDOM()
            LIMIT 2
        )
        SELECT movie_id, movie_name, genres, release_date, summary, actors, director, language, poster_path, tmdb_avg_rating, tmdb_vote_log, tmdb_popularity, distance
        FROM genre_matched
        UNION ALL
        SELECT movie_id, movie_name, genres, release_date, summary, actors, director, language, poster_path, tmdb_avg_rating, tmdb_vote_log, tmdb_popularity, distance
        FROM random_other
        ORDER BY distance;
    """)

    result = await session.execute(
        query,
        {
            "user_id": user_id,
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
            "language": row.language,
            "poster_path": row.poster_path,
            "tmdb_avg_rating": row.tmdb_avg_rating,
            "tmdb_vote_count": int(np.exp(row.tmdb_vote_log) - 1),
            "tmdb_popularity": row.tmdb_popularity
        }
        for row in movies
    ]

    return recommendations

async def check_if_movie_rated(session, user_id: str, movie_id: str):
    query = text("""
        SELECT user_rating
        FROM user_watchlist
        WHERE user_id = :user_id
        AND movie_id = :movie_id
    """)

    result = await session.execute(query, {"user_id": user_id, "movie_id": movie_id})
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Movie not in watchlist")

    return row

async def get_movie_tmdb_stats(session, movie_id: str):
    query = text("""
        SELECT tmdb_avg_rating, tmdb_vote_log, tmdb_popularity
        FROM movie_rating_stats
        WHERE movie_id = :movie_id
    """)

    result = await session.execute(query, {"movie_id": movie_id})
    row = result.first()

    if not row:
        # If movie has no stats yet, return defaults
        return 0.0, 0.0, 0.0

    return row.tmdb_avg_rating, row.tmdb_vote_log, row.tmdb_popularity

async def get_rated_movies(session, user_id: str):
    query = text("""
        SELECT 
            w.movie_id, 
            w.user_rating, 
            DATE(w.added_at) as added_at,
            m.movie_name,
            m.genres,
            m.release_date,
            m.language,
            m.poster_path
        FROM user_watchlist w
        JOIN movie_metadata m ON w.movie_id = m.movie_id
        WHERE w.user_id = :user_id
        AND w.user_rating > 0
    """)

    result = await session.execute(query, {"user_id": user_id})

    movies = result.fetchall()

    rated_movies = [
        {
            "movie_id": row.movie_id,
            "title": row.movie_name,
            "rating": row.user_rating,
            "added_at": row.added_at,
            "release_date": row.release_date,
            "genres": row.genres,
            "language": row.language,
            "poster_path": row.poster_path
        }
        for row in movies
    ]

    return rated_movies