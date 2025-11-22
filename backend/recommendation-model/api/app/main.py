from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
from db.config.conn import engine
from routes.recommendations import router as recommendation_router
from routes.user import router as user_router
from routes.movies import router as movie_router
from model.utils.cold_start_user_tower import ColdStartUserTower
from model.utils.movie_tower import MovieTower
from model.utils.reranker_model import Reranker
from middleware.cors import add_cors

# lifespan function to manage startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models once on startup
    app.state.cold_start_user_tower = ColdStartUserTower(embedding_dim=512)
    app.state.movie_tower = MovieTower(embedding_dim=512)
    app.state.reranker_model = Reranker(production=False)

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)

# middleware
add_cors(app)

app.include_router(recommendation_router)
app.include_router(user_router)
app.include_router(movie_router)

@app.get("/")
async def base():
    return {"message": "welcome to user recommendations api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
