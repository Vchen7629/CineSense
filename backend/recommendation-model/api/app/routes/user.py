from fastapi import APIRouter, Depends, HTTPException
from model.utils.cold_start_user_tower import ColdStartUserTower
from db.utils.user_sql_queries import (
    new_user_genre_embedding, 
    get_user_watchlist,
    delete_from_watchlist,
    set_user_rating_stats_stale
)
from db.utils.movies_sql_queries import (
    add_new_movie_rating,
    add_movie_metadata,
    check_if_movie_rated,
    update_movie_rating_stats,
    get_movie_tmdb_stats
)
from db.config.conn import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from utils.dependencies import get_cold_start_user_tower
from schemas.user import (
    NewUserRequest, 
    AddToWatchlistRequest, 
    RemoveFromWatchlistRequest
)

router = APIRouter(prefix="/user", tags=["user"])

# we need to create an embedding using the user tower for the
# selected top 3 genres for cold start recommendations
@router.post("/genre_embedding/{userId}")
async def new_user(
    userId: str,
    body: NewUserRequest,
    session: AsyncSession = Depends(get_session),
    user_tower: ColdStartUserTower = Depends(get_cold_start_user_tower)
):
    genres = body.genres
    user_embedding = user_tower.embedding(genres)

    await new_user_genre_embedding(session, userId, user_embedding, genres)

    return {"message": f"successfully added genre embeddings for user: {userId}"}

# fetch the movie_ids for the user that they have added to their watchlist
@router.get("/watchlist/get/{userId}")
async def get_watchlist(userId: str, session: AsyncSession = Depends(get_session)):
    watchlist = await get_user_watchlist(session, userId)

    if len(watchlist) == 0:
        raise HTTPException(
            status_code=404,
            detail="User doesnt have any movies in their watchlist"
        )
    
    return watchlist


@router.post("/watchlist/add/{userId}")
async def add_to_watchlist(
    userId: str, 
    body: AddToWatchlistRequest,
    session: AsyncSession = Depends(get_session),
):  
    movie_id = body.movie_id
    title = body.title
    genres = body.genres
    release = body.release_date
    summary = body.summary
    actors = body.actors
    director = body.director
    poster_path = body.poster_path
    rating = body.rating

    if not userId:
        raise HTTPException(status_code=404, detail="No user_id provided")

    # Convert release_date string to int year for model processing
    try:
        release_year = int(release[:4]) if isinstance(release, str) else int(release)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid release_date format. Expected YYYY or full date string.")

    await add_movie_metadata(session, movie_id, title, genres, release_year, summary, actors, director, poster_path)
    await add_new_movie_rating(session, userId, movie_id, rating)

    return {"message": "successfully added movie to watchlist!"}

@router.delete("/watchlist/remove/{userId}")
async def remove_from_watchlist(
    userId: str, 
    body: RemoveFromWatchlistRequest,
    session: AsyncSession = Depends(get_session),
):  
    movie_id = body.movie_id

    if not userId:
        raise HTTPException(status_code=404, detail="No user_id provided")

    rating = await check_if_movie_rated(session, userId, movie_id)
    was_rated = rating.user_rating > 0

    # get latest tmdb stats for that movie so we can also update the movie rating stats with the latest tmdb stats
    tmdb_avg_rating, tmdb_vote_log, tmdb_popularity = await get_movie_tmdb_stats(session, movie_id)

    # delete first so if we recalculate the deleted movie wont be there
    await delete_from_watchlist(session, userId, movie_id)
    
    # recalculate stats if movie was rated
    if was_rated:
        await update_movie_rating_stats(session, movie_id, tmdb_avg_rating, tmdb_vote_log, tmdb_popularity)

    # set the user rating stats to stale so we only need to recalculate user embeddings when showing recommendations
    await set_user_rating_stats_stale(session, userId)

    return {"message": "Successfully removed movie from watchlist!"}
