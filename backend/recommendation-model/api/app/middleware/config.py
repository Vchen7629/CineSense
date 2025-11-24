from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from pathlib import Path

# Project root (api/ directory)
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    production: bool = False
    environment: str = "development"

    database_url: str

    # AWS access
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: Optional[str] = None
    use_iam_role: bool = False

    # model file storage
    s3_bucket_name: Optional[str] = None
    s3_model_prefix: str = "models/"

    # local model paths (used during development)
    local_model_dir: str = "app/model/files_small"
    user_tower_model_name: str = "user_tower.pth"
    movie_tower_model_name: str = "movie_tower.pth"
    reranker_model_name: str = "reranker.txt"
    genre_mlb_name: str = "genre_mlb.joblib"

    # Model paths
    @property
    def user_tower_model_path(self) -> str:
        if self.production and self.s3_bucket_name:
            return f"s3://{self.s3_bucket_name}/{self.s3_model_prefix}{self.user_tower_model_name}"
        return str(PROJECT_ROOT / self.local_model_dir / self.user_tower_model_name)

    @property
    def movie_tower_model_path(self) -> str:
        if self.production and self.s3_bucket_name:
            return f"s3://{self.s3_bucket_name}/{self.s3_model_prefix}{self.movie_tower_model_name}"
        return str(PROJECT_ROOT / self.local_model_dir / self.movie_tower_model_name)

    @property
    def reranker_model_path(self) -> str:
        if self.production and self.s3_bucket_name:
            return f"s3://{self.s3_bucket_name}/{self.s3_model_prefix}{self.reranker_model_name}"
        return str(PROJECT_ROOT / self.local_model_dir / self.reranker_model_name)

    @property
    def genre_mlb_path(self) -> str:
        if self.production and self.s3_bucket_name:
            return f"s3://{self.s3_bucket_name}/{self.s3_model_prefix}{self.genre_mlb_name}"
        return str(PROJECT_ROOT / self.local_model_dir / self.genre_mlb_name)
    

    # API Settings
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:3000"]

    # Model Settings
    embedding_dim: int = 512

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()