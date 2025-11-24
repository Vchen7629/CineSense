# need to generate embeddings for all users to test user-to-user collaborative filtering accuracy
import torch
import numpy as np
import polars as pl
from shared.path_config import path_helper

class GenerateUserEmbeddings:
    def __init__(self, movie_tower, large_dataset: bool = False):
        self.embedding_dim = 512
        self.large_dataset = large_dataset
        paths = path_helper(large_dataset=large_dataset)

        self.ratings_path = paths.pos_ratings_path
        self.user_emb_path = paths.user_embedding_path

        if large_dataset:
            self.num_movies = 64548
        else:
            self.num_movies = 7363

        # Load trained movie tower
        self.movie_tower = movie_tower
        self.movie_tower.eval()

    def generate_all_user_embeddings(self):
        # Load user ratings
        user_df = pl.read_csv(self.ratings_path)

        # Group by userId
        user_to_movies = (
            user_df
            .group_by('userId')
            .agg(pl.col('movie_idx'))
            .sort('userId')
        )

        user_embeddings = []

        with torch.no_grad():
            for row in user_to_movies.iter_rows(named=True):
                user_id = row['userId']
                movie_indices = row['movie_idx']

                # Create user embedding (average of rated movies)
                movie_tensor = torch.tensor(movie_indices, device="cuda", dtype=torch.long)
                movie_embs = self.movie_tower(movie_tensor)
                user_emb = movie_embs.mean(dim=0)  # [512]

                user_emb = user_emb / user_emb.norm()

                user_embeddings.append(user_emb.cpu().numpy())

                if (user_id + 1) % 100 == 0:
                    print(f"Processed {user_id + 1} users...")

        user_embeddings = np.array(user_embeddings, dtype=np.float32)  # [num_users, 512]

        # Save
        np.save(self.user_emb_path, user_embeddings)
        print(f"Saved {user_embeddings.shape[0]} user embeddings to {self.user_emb_path}")

        return user_embeddings

if __name__ == "__main__":
    generator = GenerateUserEmbeddings(large_dataset=False)
    user_embs = generator.generate_all_user_embeddings()