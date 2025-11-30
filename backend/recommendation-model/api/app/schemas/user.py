from pydantic import BaseModel
from typing import List

class AddToWatchlistRequest(BaseModel):
    movie_id: str
    title: str
    genres: List[str]
    release_date: str
    summary: str
    actors: List[str]
    director: List[str]
    poster_path: str
    rating: float

class RemoveFromWatchlistRequest(BaseModel):
    movie_id: str

class NewUserRequest(BaseModel):
    genres: List[str]