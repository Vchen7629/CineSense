from fastapi import APIRouter, HTTPException, Depends
from typing import List
from model.utils.movie_tower import MovieTower
from db.utils.user_sql_queries import (
    regenerate_user_movie_embedding,
    update_user_ratings_stats
)
from db.utils.movies_sql_queries import (
    add_new_movie_embedding, 
    add_new_movie_rating, 
    add_movie_metadata, 
    get_movie_embeddings,
    update_movie_rating_stats
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
    release_date: int
    summary: str
    actors: List[str]
    director: List[str]
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
    
    # release date needs to be just year YYYY
    movie_embedding = movie_tower.generate_new_movie_embedding(title, genres, release, actors, director, summary)

    await add_movie_metadata(session, imdb_id, title, genres, release, summary, actors, director, poster_path)

    await add_new_movie_embedding(session, imdb_id, movie_embedding)

    is_new_rating = await add_new_movie_rating(session, user_id, imdb_id, rating)
    
    # flush so new movie rating is visible to subsequent queries in this transaction
    await session.flush()

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

    movie = await update_movie_rating_stats(session, imdb_id, tmdb_vote_avg, tmdb_vote_log, tmdb_popularity)
    user = await update_user_ratings_stats(session, user_id)
    
    return {
        "message": "Rating added" if is_new_rating else "Rating updated",
        "user_id": user_id,
        "movie_id": imdb_id,
        "rating": rating,
        "movie_test": movie,
        "user_test": user
    }



    
    
    
