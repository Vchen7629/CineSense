from pydantic_settings import BaseSettings
from pathlib import Path

# Project root (training/ directory)
PROJECT_ROOT = Path(__file__).parent.parent
API_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

user_tower_model_name: str = "user_tower.pth"
movie_tower_model_name: str = "movie_tower.pth"
reranker_model_name: str = "reranker-model.txt"
genre_mlb_joblib: str = "genre_mlb.joblib"

pos_ratings_csv: str = "user-positive-ratings.csv"
neg_ratings_csv: str = "user-negative-ratings.csv"
top3_genres_csv: str = "user-top3-genres.csv"
pruned_movies_csv: str = "movie-output.csv"
movie_metadata_csv: str = "movie-metadata.csv"
movie_embedding_npy: str = "movie_embeddings.npy"
movie_title_embedding_npy: str = "title_embeddings.npy"
movie_reranker_features_csv: str = "reranker-movie-features.csv"
movie_genre_mlb_npy: str = "genre_mlb.npy"
movie_normalized_year_npy: str = "movie_year.npy"
movie_overview_dir_cast_embeddings_npy: str = "overview_dir_cast_embeddings.npy"
user_embedding_npy: str = "user-embeddings.npy"
user_reranker_features_csv: str = "reranker-user-features.csv"
user_favorite_actor_dir_csv: str = "favorite-actor-directors.csv"
user_cold_start_negatives_csv: str = "user-cold-start-negatives.csv"
user_collaborative_negatives_csv: str = "user-collaborative-negatives.csv"
user_preferred_genres_npy: str = "preferred-genres.npy"
not_found_imdb_csv: str = "not-found-imdb.csv"
missing_movie_metadata_csv: str = "missing-metadata.csv"

tmdb_all_movies_csv: str = "TMDB_all_movies.csv"
tmdb_all_movies_cleaned_csv: str = "TMDB_all_movies_cleaned.csv"

movielens_movies_csv: str = "movies.csv"
movielens_links_csv: str = "links.csv"
movielens_ratings_csv: str = "ratings.csv"

imdb_mismatches_csv: str = "imdb_mismatches.csv"
duplicate_tmdbId_csv: str = "duplicate_id.csv"

class Paths(BaseSettings):
    large_dataset: bool = False
    metadata_dir: str = "datasets/metadata"

    # Directories
    @property
    def local_model_dir(self) -> str:
        return "datasets/model-files" if self.large_dataset else "datasets/model-files-small"
    
    @property
    def output_dir(self) -> str:
        return "datasets/output" if self.large_dataset else "datasets/output-small"
    
    @property
    def movielens_dir(self) -> str:
        return "datasets/ml-latest" if self.large_dataset else "datasets/ml-latest-small"
    
    @property
    def cleaning_files_dir(self) -> str:
        return "datasets/cleaning-files" if self.large_dataset else "datasets/cleaning-files-small"
    
    @property
    def api_model_dir(self) -> Path:
        subdir = "files" if self.large_dataset else "files_small"
        return API_ROOT / "api" / "app" / "model" / subdir

    # Model paths
    @property
    def user_tower_model_path(self) -> str:
        return str(PROJECT_ROOT / self.local_model_dir / user_tower_model_name)

    @property
    def movie_tower_model_path(self) -> str:
        return str(PROJECT_ROOT / self.local_model_dir / movie_tower_model_name)

    @property
    def reranker_model_path(self) -> str:
        return str(PROJECT_ROOT / self.local_model_dir / reranker_model_name)

    @property
    def genre_mlb_path(self) -> str:
        return str(PROJECT_ROOT / self.local_model_dir / genre_mlb_joblib)
    
    # api folder paths 
    @property
    def user_tower_model_api_path(self) -> str:
        return str(PROJECT_ROOT / self.api_model_dir / user_tower_model_name)

    @property
    def movie_tower_model_api_path(self) -> str:
        return str(PROJECT_ROOT / self.api_model_dir / movie_tower_model_name)

    @property
    def reranker_model_api_path(self) -> str:
        return str(PROJECT_ROOT / self.api_model_dir / reranker_model_name)

    @property
    def genre_mlb_api_path(self) -> str:
        return str(PROJECT_ROOT / self.api_model_dir / genre_mlb_joblib)
    
    # output file paths
    @property
    def pos_ratings_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / pos_ratings_csv)
    
    @property
    def neg_ratings_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / neg_ratings_csv)

    @property
    def top3_genres_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / top3_genres_csv)

    @property
    def pruned_movies_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / pruned_movies_csv)
    
    @property
    def movie_metadata_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / movie_metadata_csv)
    
    @property
    def movie_embedding_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / movie_embedding_npy)
    
    @property
    def movie_title_embeddings_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / movie_title_embedding_npy)

    @property
    def movie_genre_mlb_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / movie_genre_mlb_npy)
    
    @property
    def movie_year_normalized_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / movie_normalized_year_npy)

    @property
    def movie_overview_dir_cast_embeddings_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / movie_overview_dir_cast_embeddings_npy)

    @property
    def movie_reranker_features_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / movie_reranker_features_csv)
    
    @property
    def user_embedding_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / user_embedding_npy)
    
    @property
    def user_reranker_features_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / user_reranker_features_csv)
    
    @property
    def user_favorite_actor_dir_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / user_favorite_actor_dir_csv)
    
    @property
    def user_cold_start_negatives_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / user_cold_start_negatives_csv)
    
    @property
    def user_collaborative_negatives_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / user_collaborative_negatives_csv)
    
    @property
    def user_preferred_genres_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / user_preferred_genres_npy)

    @property
    def not_found_imdb_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / not_found_imdb_csv)
    
    @property
    def missing_movie_metadata_path(self) -> str:
        return str(PROJECT_ROOT / self.output_dir / missing_movie_metadata_csv)
    
    @property
    def tmdb_all_movies_path(self) -> str:
        return str(PROJECT_ROOT / self.metadata_dir / tmdb_all_movies_csv)

    @property
    def tmdb_all_movies_cleaned_path(self) -> str:
        return str(PROJECT_ROOT / self.metadata_dir / tmdb_all_movies_cleaned_csv)

    # movielens paths
    @property
    def movielens_movies_path(self) -> str:
        return str(PROJECT_ROOT / self.movielens_dir / movielens_movies_csv)

    @property
    def movielens_links_path(self) -> str:
        return str(PROJECT_ROOT / self.movielens_dir / movielens_links_csv)

    @property
    def movielens_ratings_path(self) -> str:
        return str(PROJECT_ROOT / self.movielens_dir / movielens_ratings_csv)
    
    # preprocessing cleaning files paths
    @property
    def imdb_mismatches_path(self) -> str:
        return str(PROJECT_ROOT / self.cleaning_files_dir / imdb_mismatches_csv)
    
    @property
    def duplicate_tmdbId_path(self) -> str:
        return str(PROJECT_ROOT / self.cleaning_files_dir / duplicate_tmdbId_csv)


def path_helper(large_dataset: bool = False) -> Paths:
    return Paths(large_dataset=large_dataset)
