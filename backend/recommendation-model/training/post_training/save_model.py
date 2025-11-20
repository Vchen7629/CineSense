import os
import torch
import torch.nn.functional as f
import numpy as np
import psycopg2
import polars as pl

class SaveModel:
    def __init__(self, user_tower, movie_tower, num_movies: int, large_dataset: bool = False, personalized: bool = True):
        current_dir = os.path.dirname(__file__)
        self.personalized = personalized

        if large_dataset:
            api_dir = os.path.join(current_dir, "..", "..", "api", "app", "model", "files")
            self.user_tower_path = os.path.join(api_dir, "user_tower.pth")
            self.movie_tower_path = os.path.join(api_dir, "movie_tower.pth")
            self.movie_metadata_path = os.path.join(current_dir, "..", "datasets", "output", "movie-metadata.csv")
            if self.personalized:
                self.movie_emb_path = os.path.join(current_dir, "..", "datasets", "output", "movie_embeddings.npy")
        else:
            api_dir = os.path.join(current_dir, "..", "..", "api", "app", "model", "files_small")
            self.user_tower_path = os.path.join(api_dir, "user_tower.pth")
            self.movie_tower_path = os.path.join(api_dir, "movie_tower.pth")
            self.movie_metadata_path = os.path.join(current_dir, "..", "datasets", "output-small", "movie-metadata.csv")
            if self.personalized:
                self.movie_emb_path = os.path.join(current_dir, "..", "datasets", "output-small", "movie_embeddings.npy")

        self.movie_tower = movie_tower
        self.user_tower = user_tower
        self.num_movies = num_movies
    
    # save user and movie towers to .pth files
    def _save_towers(self) -> None:
        # user tower may or may not be saved since only cold start requires the tower to be saved
        if self.user_tower:
            user_tower = self.user_tower._orig_mod if hasattr(self.user_tower, '_orig_mod') else self.user_tower
            torch.save(user_tower.state_dict(), self.user_tower_path) # Save only state_dict (weights)

        # movie tower is only required to be saved when saving the collaborative filtering model due to
        # it being required for creating embeddings for new unseen movies
        if self.personalized:
            movie_tower = self.movie_tower._orig_mod if hasattr(self.movie_tower, '_orig_mod') else self.movie_tower
            torch.save(movie_tower.state_dict(), self.movie_tower_path)  # Save only state_dict (weights)

    def _precompute_embeddings(self):
        with torch.no_grad(): # precompute all movie embeddings
            movie_indices = torch.arange(self.num_movies, dtype=torch.long, device="cuda")
            movie_embeddings = self.movie_tower(movie_indices)
            movie_embeddings = f.normalize(movie_embeddings, dim=1)

        # save embedding file
        if self.personalized:
            np.save(self.movie_emb_path, movie_embeddings.cpu())

        return movie_embeddings
    
    # save the embeddings into the postgres
    def _save_to_postgres(self, embeddings, db_config: dict[str, str]):
        metadata_df = pl.read_csv(self.movie_metadata_path, dtypes={"tmdbId": pl.Utf8})
        conn = psycopg2.connect(**db_config)
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

    def save_all(self, save_to_db: bool = False, db_config: dict = None):
        self._save_towers() # save tower models
        
        # movie embeddings
        embeddings = self._precompute_embeddings()

        # Optionally: save to embeddings to postgres db
        if save_to_db:
            self._save_to_postgres(embeddings, db_config)
    

