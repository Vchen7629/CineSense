import numpy as np
import os
import polars as pl
import torch
import torch.nn.functional as f
from typing import List
from collections import Counter

# class with helper functions for testing accuracy of the candidate generation two tower
# model which fetches candidates (movies) based on similar users using cosine similarity
class CandidateGenerationModelEval:
    def __init__(self, movie_tower, large_dataset: bool = False):
        
        current_dir = os.path.dirname(__file__)

        if large_dataset:
            movie_embeddings_path = os.path.join(current_dir, "..", "datasets", "output", "movie_embeddings.npy")
            user_ratings_path = os.path.join(current_dir, "..", "datasets", "output", "user-output.csv")
            user_emb_path = os.path.join(current_dir, "..", "datasets", "eval-files", "user-embeddings.npy")
        else:
            movie_embeddings_path = os.path.join(current_dir, "..", "datasets", "output-small", "movie_embeddings.npy")
            user_ratings_path = os.path.join(current_dir, "..", "datasets", "output-small", "user-output.csv")
            user_emb_path = os.path.join(current_dir, "..", "datasets", "eval-files", "user-embeddings-small.npy")

        # Load precomputed movie embeddings
        self.movie_embeddings = np.load(movie_embeddings_path)

        # Read user ratings CSV
        user_df = pl.read_csv(user_ratings_path)

        # Group by userId and aggregate movie_idx into lists
        grouped = user_df.group_by('userId').agg(pl.col('movie_idx'))

        # Convert to dict for easier access
        self.user_to_movies = {
            row['userId']: row['movie_idx']
            for row in grouped.iter_rows(named=True)
        }

        # load user embeddings to test user-user collaborative accuracy
        self.user_embeddings = np.load(user_emb_path)

        self.movie_tower = movie_tower
        self.movie_tower.eval()

        print(f"Found {len(self.user_to_movies)} users with ratings")

    # Evaluae collaborative filtering by using leave-one-out to test hitrate for 
    # user-user similarity (collaborative filtering)
    # k: Top-K for hitrate
    # num_similar_users: number of similar users to find
    # candidate_pool_size: size of candidate pool from similar users 
    def leave_one_out_evaluation_with_user_similarity(
        self,
        k: int = 10,
        num_similar_users: int = 100,
        candidate_pool_size: int = 300
    ) -> None:
        hits = 0
        total = 0  # Track only evaluated users

        for user_id, movies in self.user_to_movies.items():
            if len(movies) < 2:
                continue

            # Leave-one-out: hold out last movie
            train_movies = movies[:-1]
            test_movie = movies[-1]

            # Create target user embedding
            train_movie_tensor = torch.tensor(train_movies, device="cuda", dtype=torch.long)
            train_movie_embs = self.movie_tower(train_movie_tensor)
            target_user_emb = train_movie_embs.mean(dim=0)  # [512]

            # === USER-USER STAGE ===
            # Normalize for cosine similarity
            target_user_emb_norm = target_user_emb / target_user_emb.norm()
            target_user_emb_np = target_user_emb_norm.cpu().detach().numpy()

            # Compute cosine similarity to all other users (assumes user_embeddings are normalized)
            similarities = np.dot(self.user_embeddings, target_user_emb_np)  # [num_users]
            similarities[user_id] = -np.inf  # Exclude self

            # Get top-K similar users
            similar_user_indices = np.argsort(similarities)[-num_similar_users:][::-1]

            # Collect movies from similar users with frequency counts
            candidate_movie_counts = Counter()
            for similar_user_id in similar_user_indices:
                similar_user_movies = self.user_to_movies[similar_user_id]
                for movie in similar_user_movies:
                    if movie not in train_movies:  # Exclude already rated
                        candidate_movie_counts[movie] += 1

            if len(candidate_movie_counts) == 0:
                continue

            # Sort by frequency (most popular among similar users first)
            candidate_movies = [movie for movie, count in candidate_movie_counts.most_common(candidate_pool_size)]

            # === RANKING STAGE ===
            # Rank candidates using movie embeddings
            candidate_tensor = torch.tensor(candidate_movies, device="cuda", dtype=torch.long)
            candidate_embs = self.movie_tower(candidate_tensor)

            # Normalize
            target_user_emb_norm_expanded = f.normalize(target_user_emb.unsqueeze(0), dim=1)
            candidate_embs_norm = f.normalize(candidate_embs, dim=1)

            # Compute similarities
            scores = (target_user_emb_norm_expanded @ candidate_embs_norm.T).squeeze(0)  # [num_candidates]

            # Get top-k
            top_k_indices = torch.topk(scores, min(k, len(candidate_movies))).indices
            top_k_movies = [candidate_movies[i] for i in top_k_indices.cpu().tolist()]

            # Check if test movie is in top-k
            if test_movie in top_k_movies:
                hits += 1

            total += 1  # Count this user as evaluated

        hitrate = hits / total if total > 0 else 0.0
        print(f"User-User CF HitRate@{k}: {hitrate:.4f} ({hitrate*100:.2f}%)")
        print(f"  Evaluated users: {total}")
        print(f"  Hits: {hits}")
        print(f"  Num similar users: {num_similar_users}")
        print(f"  Candidate pool size: {candidate_pool_size}")
        return hitrate


