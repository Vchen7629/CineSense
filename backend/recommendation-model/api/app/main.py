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
from utils.env_config import settings
from utils.download_model_files import download_recommendation_model_files
from utils.load_model_files import load_sentence_transformer_model, load_recommendation_models
import logging

# set up logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# lifespan function to manage startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CineSense Recommendation API")
    try:
        download_recommendation_model_files()
    except Exception as e:
        logger.error(f"❌ Failed to download models from S3: {e}")
        raise

    # Load models once on startup
    logger.info("Loading ML models...")

    (
        user_tower_path, 
        movie_tower_path, 
        genre_mlb, 
        reranker_model_path
    ) = load_recommendation_models()

    sentence_transformer_model = load_sentence_transformer_model()
    app.state.cold_start_user_tower = ColdStartUserTower(user_tower_path, genre_mlb)
    app.state.movie_tower = MovieTower(movie_tower_path, genre_mlb, sentence_transformer_model)
    app.state.reranker_model = Reranker(reranker_model_path)
    logger.info("Models loaded successfully")

    yield

    logger.info("Shutting down...")
    await engine.dispose()
    logger.info("Shutdown complete!!!")

app = FastAPI(lifespan=lifespan)

# middleware
add_cors(app)

logger.info("Registering routes")
app.include_router(recommendation_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(movie_router, prefix="/api")
logger.info("Routes registered Successfully!")

@app.get("/api")
async def base():
    return {"message": "welcome to user recommendations api"}

@app.get("/api/health")
async def health():
    return {"status": "healthy!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
