from fastapi import APIRouter, HTTPException, Depends
from typing import List
from model.utils.movie_tower import MovieTower
from db.utils.user_sql_queries import set_user_rating_stats_stale
from db.utils.movies_sql_queries import (
    add_new_movie_embedding, 
    add_new_movie_rating, 
    add_movie_metadata,
    update_movie_rating_stats,
    get_watchlist_movies
)
from db.config.conn import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from utils.dependencies import get_movie_tower
import numpy as np

router = APIRouter(prefix="/movie", tags=["movie"])

class RateMovieRequest(BaseModel):
    user_id: str
    title: str
    genres: List[str]
    release_date: str
    summary: str
    actors: List[str]
    director: List[str]
    language: str
    poster_path: str
    rating: float
    tmdb_vote_avg: float
    tmdb_vote_count: float
    tmdb_popularity: float

@router.post("/rate/{imdb_id}")
async def new_rated_movie(
    imdb_id: str, 
    body: RateMovieRequest,
    movie_tower: MovieTower = Depends(get_movie_tower),
    session: AsyncSession = Depends(get_session),
):  
    user_id = body.user_id
    title = body.title
    genres = body.genres
    release = body.release_date
    summary = body.summary
    actors = body.actors
    director = body.director
    language = body.language
    poster_path = body.poster_path
    rating = body.rating
    tmdb_vote_avg = body.tmdb_vote_avg
    tmdb_vote_count = body.tmdb_vote_count
    tmdb_popularity = body.tmdb_popularity

    tmdb_vote_log = np.log1p(tmdb_vote_count)

    if not user_id:
        raise HTTPException(status_code=404, detail="No user_id provided")

    if not rating:
        raise HTTPException(status_code=404, detail="No rating provided")

    # Convert release_date string to int year for model processing
    try:
        release_year = int(release[:4]) if isinstance(release, str) else int(release)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid release_date format. Expected YYYY or full date string.")

    # release date needs to be just year YYYY
    movie_embedding = movie_tower.generate_new_movie_embedding(title, genres, release_year, actors, director, summary)

    await add_movie_metadata(session, imdb_id, title, genres, release_year, summary, actors, director, language, poster_path)

    await add_new_movie_embedding(session, imdb_id, movie_embedding)

    is_new_rating = await add_new_movie_rating(session, user_id, imdb_id, rating)

    await update_movie_rating_stats(session, imdb_id, tmdb_vote_avg, tmdb_vote_log, tmdb_popularity)

    # set the user rating stats table is_stale to true so we don't have to recalculate
    # the user embeddings each time a user rates a movie, we'll recalculate it in 
    # the recommendations route
    await set_user_rating_stats_stale(session, user_id)
    
    return {
        "message": "Rating added" if is_new_rating else "Rating updated",
        "user_id": user_id,
        "movie_id": imdb_id,
        "rating": rating
    }

@router.get("/get_watchlist/{user_id}")
async def get_user_watchlist_movies(user_id: str, session: AsyncSession = Depends(get_session)):
    if not user_id:
        raise HTTPException(status_code=404, detail="No user_id provided")
    
    watchlist_movies = await get_watchlist_movies(session, user_id)

    return watchlist_movies