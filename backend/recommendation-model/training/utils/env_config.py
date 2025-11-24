from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path

# Project root (api/ directory)
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    TMDB_API_KEY: str

    # AWS access
    aws_region: Optional[str] = "us-west-1"
    aws_access_key: str
    aws_secret_access_key: str

    # model file storage
    s3_bucket_name: Optional[str] = None
    # choose between
    # - models/production/v1 - trained and tested trained model files
    # - models/development/v1 - testing model files
    s3_model_prefix_prod: str = "models/production/v1"

    # local model paths (used during development)
    local_model_dir: str = "datasets/model-files-small"
    user_tower_model_name: str = "user_tower.pth"
    movie_tower_model_name: str = "movie_tower.pth"
    reranker_model_name: str = "reranker-model.txt"
    genre_mlb_name: str = "genre_mlb.joblib"

    # Model paths
    @property
    def user_tower_model_path(self) -> str:
        return str(PROJECT_ROOT / self.local_model_dir / self.user_tower_model_name)

    @property
    def movie_tower_model_path(self) -> str:
        return str(PROJECT_ROOT / self.local_model_dir / self.movie_tower_model_name)

    @property
    def reranker_model_path(self) -> str:
        if self.production and self.s3_bucket_name:
            return f"/tmp/models/{self.reranker_model_name}"
        return str(PROJECT_ROOT / self.local_model_dir / self.reranker_model_name)

    @property
    def genre_mlb_path(self) -> str:
        if self.production and self.s3_bucket_name:
            return f"/tmp/models/{self.genre_mlb_name}"
        return str(PROJECT_ROOT / self.local_model_dir / self.genre_mlb_name)

    # Model Settings
    embedding_dim: int = 512

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()