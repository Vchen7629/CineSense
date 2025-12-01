import torch
import torch.nn.functional as f
import numpy as np
import psycopg2
import polars as pl
from shared.path_config import path_helper

class SaveModel:
    def __init__(self, user_tower, movie_tower, num_movies: int, large_dataset: bool = False, personalized: bool = True):
        self.personalized = personalized
        paths = path_helper(large_dataset=False)

        self.user_tower_api_path = paths.user_tower_model_api_path
        self.user_tower_s3_path = paths.user_tower_model_path
        self.movie_tower_api_path = paths.movie_tower_model_api_path
        self.movie_tower_s3_path = paths.movie_tower_model_path
        self.movie_metadata_path = paths.movie_metadata_path

        if self.personalized:
            self.movie_emb_path = paths.movie_embedding_path

        self.movie_tower = movie_tower
        self.user_tower = user_tower
        self.num_movies = num_movies

        self.db_config = {
            "dbname": "example_db",
            "user": "postgres",
            "password": "password",
            "host": "localhost",
            "port": 5432
        }
    
    # save user and movie towers to .pth files
    def _save_towers(self) -> None:
        # user tower may or may not be saved since only cold start requires the tower to be saved
        if self.user_tower:
            user_tower = self.user_tower._orig_mod if hasattr(self.user_tower, '_orig_mod') else self.user_tower
            
            # Save only state_dict (weights) files to both api folder and dataset folder
            torch.save(user_tower.state_dict(), self.user_tower_api_path)
            #torch.save(user_tower.state_dict(), self.user_tower_s3_path)

        # movie tower is only required to be saved when saving the collaborative filtering model due to
        # it being required for creating embeddings for new unseen movies
        if self.personalized:
            movie_tower = self.movie_tower._orig_mod if hasattr(self.movie_tower, '_orig_mod') else self.movie_tower
            
            # Save only state_dict (weights) files to both api folder and dataset folder
            torch.save(movie_tower.state_dict(), self.movie_tower_api_path)
            #torch.save(movie_tower.state_dict(), self.movie_tower_s3_path)

    def _precompute_embeddings(self):
        with torch.no_grad(): # precompute all movie embeddings
            movie_indices = torch.arange(self.num_movies, dtype=torch.long, device="cuda")
            movie_embeddings = self.movie_tower(movie_indices)
            movie_embeddings = f.normalize(movie_embeddings, dim=1)

        return movie_embeddings
    
    # save the embeddings into the postgres
    def _save_movie_embeddings_local_postgres(self, embeddings):
        metadata_df = pl.read_csv(self.movie_metadata_path, dtypes={"tmdbId": pl.Utf8})
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        # join embedding vector with the metadata df 
        metadata_df = metadata_df.with_columns([
            pl.Series("embedding", [emb.tolist() for emb in embeddings])
        ])

        # insert into postgres
        for row in metadata_df.iter_rows(named=True):
            # insert movie metadata into movie_metadata table
            cursor.execute("""
                INSERT INTO movie_metadata (
                    movie_id, movie_name, genres, release_date, summary, actors, director, poster_path
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (movie_id) DO NOTHING
            """, (
                str(row['tmdbId']),
                row['title'],
                row['genres_normalized'].split("|"),
                row['year'],
                row['overview'],
                row['cast_normalized'].split("|"),
                row['director'].split("|"),
                row['poster_path']
            ))

            # Insert TMDB rating Stats into movie_rating_stats table
            vote_count = row.get('vote_count', 0.0)
            vote_count_log = float(np.log1p(vote_count))

            cursor.execute("""
                INSERT INTO movie_rating_stats (
                    movie_id, tmdb_avg_rating, tmdb_vote_log, tmdb_popularity
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (movie_id) DO NOTHING
            """, (
                str(row['tmdbId']),
                float(row.get('vote_average', 0.0)),
                vote_count_log,
                float(row.get('popularity', 0.0))
            ))

            # insert embedding into correct movie_embedding table depending on whether its the
            # personalized or cold start
            if self.personalized:
                cursor.execute("""
                    INSERT INTO movie_embedding_personalized (movie_id, embedding)
                    VALUES (%s, %s::vector)
                """, (
                    str(row['tmdbId']),
                    row['embedding']
                ))
            else:
                cursor.execute("""
                    INSERT INTO movie_embedding_coldstart (movie_id, embedding)
                    VALUES (%s, %s::vector)
                """, (
                    str(row['tmdbId']),
                    row['embedding']
                ))

        # debug
        print(metadata_df)

        # add to database
        conn.commit()
        rows = cursor.execute("select * from movie_metadata")
        print(rows)

    # save function called by training script to save model files after training
    # can pass the following arguments
    #   - mode: either dev or prod, switch to dec
    def save_all(self, save_to_local_db: bool = False):
        self._save_towers() # save tower models
        
        # movie embeddings
        movie_embeddings = self._precompute_embeddings()

        # save embedding file
        if self.personalized:
            np.save(self.movie_emb_path, movie_embeddings.cpu())


        # Optionally: save to embeddings to postgres db
        if save_to_local_db:
            self._save_movie_embeddings_local_postgres(movie_embeddings)
    

