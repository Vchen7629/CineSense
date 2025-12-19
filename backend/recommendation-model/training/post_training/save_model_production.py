import boto3
import os
from datetime import datetime
from utils.env_config import settings
from shared.path_config import path_helper
import numpy as np
import polars as pl
from io import BytesIO
import torch
import torch.nn.functional as f

class SaveModelProd:
    def __init__(
        self,
        model_version: str,
        collaborative: bool,
        cold_start: bool,
        reranker: bool,
        movie_tower = None,
        num_movies: int = None,
        large_dataset: bool = False
    ) -> None:
        self.collaborative = collaborative
        self.cold_start = cold_start
        self.reranker = reranker
        self.movie_tower = movie_tower
        self.num_movies = num_movies

        self.paths = path_helper(large_dataset)

        # Create S3 client with credentials
        self.s3_client = boto3.client(
            's3',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_access_key
        )

        # Generate version tag if not provided
        if model_version is None:
            model_version = datetime.now().strftime('%Y%m%d-%H%M%S')

        self.model_version = model_version

        # S3 bucket and prefix
        self.s3_bucket = settings.s3_bucket_name or 'cinesense-ml-artifacts-prod'
        self.s3_model_files_prefix = f"models/production/{model_version}"
        self.s3_movie_embeddings_cold_start_prefix = f"movie_embeddings/cold_start/production/{model_version}"
        self.s3_movie_embeddings_collaborative_prefix = f"movie_embeddings/collaborative/production/{model_version}"
        self.s3_movie_metadata_prefix = f"movie_metadata/production/{model_version}"
        self.s3_movie_ratings_prefix = f"movie_ratings/production/{model_version}"

    def _precompute_embeddings(self) -> torch.tensor:
        """Precompute all movie embeddings from movie tower"""
        if self.movie_tower is None or self.num_movies is None:
            raise ValueError("movie_tower and num_movies required for embedding generation")

        print("Precomputing movie embeddings...")
        with torch.no_grad():
            movie_indices = torch.arange(self.num_movies, dtype=torch.long, device="cuda")
            movie_embeddings = self.movie_tower(movie_indices)
            movie_embeddings = f.normalize(movie_embeddings, dim=1)

        print(f"Computed {len(movie_embeddings)} movie embeddings")
        return movie_embeddings

    def _save_movie_embeddings_s3(self, embeddings: torch.tensor, file_name: str):
        """Save movie embeddings as .npy file to S3"""
        buffer = BytesIO()
        np.save(buffer, embeddings.cpu().numpy())
        buffer.seek(0)

        if self.collaborative:
            s3_key = f"{self.s3_movie_embeddings_collaborative_prefix}/{file_name}"
        
        if self.cold_start:
            s3_key = f"{self.s3_movie_embeddings_cold_start_prefix}/{file_name}"

        self.s3_client.upload_fileobj(
            buffer,
            self.s3_bucket,
            s3_key
        )
        print(f"Uploaded embeddings to s3://{self.s3_bucket}/{s3_key}")

    def _save_dataframe_s3(self, df: pl.DataFrame, file_name: str):
        """Save Polars DataFrame as CSV to S3"""
        buffer = BytesIO()
        df.write_csv(buffer)
        buffer.seek(0)

        if file_name == "movie_metadata.csv":
            s3_key = f"{self.s3_movie_metadata_prefix}/{file_name}"
        if file_name == "movie_rating_stats.csv":
            s3_key = f"{self.s3_movie_ratings_prefix}/{file_name}"

        self.s3_client.upload_fileobj(
            buffer,
            self.s3_bucket,
            s3_key
        )
        print(f"Uploaded {file_name} ({len(df)} rows) to s3://{self.s3_bucket}/{s3_key}")
    
    def _save_model_file_s3(self, file_path: str, file_name: str):
        """Upload a model file from disk to S3"""
        if not os.path.exists(file_path):
            print(f"Warning: {file_name} not found at {file_path}")
            return

        s3_key = f"{self.s3_model_files_prefix}/{file_name}"
        print(f"Uploading {file_name}...")

        try:
            self.s3_client.upload_file(
                Filename=file_path,
                Bucket=self.s3_bucket,
                Key=s3_key,
                ExtraArgs={'ServerSideEncryption': 'AES256'}
            )
            print(f"Uploaded to s3://{self.s3_bucket}/{s3_key}")
        except Exception as e:
            print(f"Failed to upload {file_name}: {e}")
            raise

    def _prepare_movie_metadata(self):
        """
        Prepare movie metadata DataFrames with Polars filtering.
        Returns: (metadata_df, rating_stats_df)
        """
        print("Loading movie metadata CSV...")
        metadata_df = pl.read_csv(self.paths.movie_metadata_path, dtypes={"tmdbId": pl.Utf8})

        print(f"Loaded {len(metadata_df)} movies from metadata")

        # Prepare movie_metadata table data (select specific columns)
        movie_metadata_df = metadata_df.select([
            pl.col("tmdbId"),
            pl.col("title"),
            pl.col("genres_normalized"),
            pl.col("year"),
            pl.col("overview"),
            pl.col("cast_normalized"),
            pl.col("director"),
            pl.col("original_language"),
            pl.col("poster_path")
        ])

        # Prepare movie_rating_stats table data
        rating_stats_df = metadata_df.select([
            pl.col("tmdbId").alias("movie_id"),
            pl.col("vote_average").cast(pl.Float64).fill_null(0.0),
            (pl.col("vote_count").cast(pl.Float64).fill_null(0.0).log1p()),
            pl.col("popularity").cast(pl.Float64).fill_null(0.0)
        ])

        print(f"Prepared {len(movie_metadata_df)} metadata rows")
        print(f"Prepared {len(rating_stats_df)} rating stats rows")

        return movie_metadata_df, rating_stats_df

    def save_all(self):
        """
        Main method to save all necessary files to S3.
        Saves model files, embeddings, and metadata CSVs.
        """
        print(f"\n{'='*60}")
        print(f"Starting S3 upload for version: {self.model_version}")
        print(f"{'='*60}\n")

        movie_tower_file_path = self.paths.movie_tower_model_path
        user_tower_file_path = self.paths.user_tower_model_path
        reranker_model_file_path = self.paths.reranker_model_path
        genre_mlb_path = self.paths.genre_mlb_path

        if self.collaborative:
            print("\n--- Saving Collaborative Filtering Artifacts ---")
            self._save_model_file_s3(movie_tower_file_path, "movie_tower.pth")
            self._save_model_file_s3(genre_mlb_path, "genre_mlb.joblib")

            # Precompute embeddings from movie tower
            embeddings = self._precompute_embeddings()

            # Prepare metadata with Polars
            metadata_df, rating_stats_df = self._prepare_movie_metadata()

            # Save to S3
            self._save_movie_embeddings_s3(embeddings, "movie_embeddings_collaborative.npy")

        if self.cold_start:
            print("\n--- Saving Cold Start Artifacts ---")
            self._save_model_file_s3(user_tower_file_path, "user_tower.pth")
            self._save_model_file_s3(genre_mlb_path, "genre_mlb.joblib")

            # Precompute embeddings from movie tower
            embeddings = self._precompute_embeddings()

            # Prepare metadata and embeddings with Polars
            metadata_df, rating_stats_df = self._prepare_movie_metadata()

            # Save to S3
            self._save_movie_embeddings_s3(embeddings, "movie_embeddings_coldstart.npy")
            self._save_dataframe_s3(metadata_df, "movie_metadata.csv")
            self._save_dataframe_s3(rating_stats_df, "movie_rating_stats.csv")

        if self.reranker:
            print("\n--- Saving Reranker Artifacts ---")
            self._save_model_file_s3(reranker_model_file_path, "reranker-model.txt")

        print(f"\n{'='*60}")
        print(f"Successfully uploaded all files to S3")
        print(f"Version: {self.model_version}")
        print(f"{'='*60}\n")

