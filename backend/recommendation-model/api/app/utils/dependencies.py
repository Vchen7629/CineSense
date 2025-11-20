from fastapi import Request
from model.utils.cold_start_user_tower import ColdStartUserTower
from model.utils.movie_tower import MovieTower

# Dependency to get the pre-loaded cold start usertower
def get_cold_start_user_tower(request: Request) -> ColdStartUserTower:
    return request.app.state.cold_start_user_tower

# Dependency to get the pre-loaded movie tower
def get_movie_tower(request: Request) -> MovieTower:
    return request.app.state.movie_tower