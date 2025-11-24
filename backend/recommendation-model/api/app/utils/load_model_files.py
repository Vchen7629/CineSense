import joblib
from pathlib import Path
from sentence_transformers import SentenceTransformer
from utils.env_config import settings
import logging

logger = logging.getLogger(__name__)

# load SentenceTransformer model
# in prod: uses bundled model from /app/models bundled during docker build
# in dev: uses huggingface model
def load_sentence_transformer_model() -> SentenceTransformer:
    if settings.production:
        model_path = "/app/models/multilingual-e5-small"
        logger.info(f"Loading production model from {model_path}")

        if not Path(model_path).exists():
            raise FileNotFoundError(f"Bundled model not found: {model_path}")
        
        model = SentenceTransformer(model_path, local_files_only=True)

    else:
        model_name = settings.hf_model_name
        logger.info(f"Loading dev model: {settings.hf_model_name}")
        model = SentenceTransformer(model_name)

    logger.info("Sentence Transformer model loaded successfully")
    return model

def load_recommendation_models():
    user_tower_path = settings.user_tower_model_path
    movie_tower_path = settings.movie_tower_model_path
    genre_mlb_path = settings.genre_mlb_path
    reranker_model_path = settings.reranker_model_path

    if not Path(user_tower_path).exists():
        raise FileNotFoundError(f"user tower model not found: {user_tower_path}")
    if not Path(movie_tower_path).exists():
        raise FileNotFoundError(f"movie tower model not found: {movie_tower_path}")
    if not Path(genre_mlb_path).exists():
        raise FileNotFoundError(f"genre mlb not found: {genre_mlb_path}")
    if not Path(reranker_model_path).exists():
        raise FileNotFoundError(f"reranker tower model not found: {reranker_model_path}")

    genre_mlb = joblib.load(genre_mlb_path)

    return user_tower_path, movie_tower_path, genre_mlb, reranker_model_path



