import numpy as np
import polars as pl
import torch
import torch.nn.functional as f
from collections import Counter
from tqdm import tqdm
from shared.path_config import path_helper

# class with helper functions for testing accuracy of the candidate generation two tower
# model which fetches candidates (movies) based on similar users using cosine similarity
class CandidateGenerationModelEval:
    def __init__(self, large_dataset: bool = False):
        paths = path_helper(large_dataset=large_dataset)

        movie_embeddings_path = paths.movie_embedding_path
        user_ratings_path = paths.pos_ratings_path
        user_emb_path = paths.user_embedding_path

        # Load precomputed movie embeddings and convert to torch tensor
        movie_embeddings_np = np.load(movie_embeddings_path)
        self.movie_embeddings = torch.tensor(movie_embeddings_np, dtype=torch.float32, device="cuda")

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

        print(f"Found {len(self.user_to_movies)} users with ratings")
        print(f"Loaded {self.movie_embeddings.shape[0]} pre-computed movie embeddings")

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

        # Pre-convert all user movie lists to sets for fast lookup
        user_to_movies_set = {
            user_id: set(movies)
            for user_id, movies in self.user_to_movies.items()
        }

        # Progress bar
        pbar = tqdm(self.user_to_movies.items(), desc=f"Evaluating (K={k}, SimUsers={num_similar_users}, Pool={candidate_pool_size})")

        for user_id, movies in pbar:
            if len(movies) < 2:
                continue

            # Leave-one-out: hold out last movie
            train_movies = movies[:-1]
            test_movie = movies[-1]

            train_movies_set = set(train_movies)

            # Create target user embedding using pre-computed embeddings
            train_movie_embs = self.movie_embeddings[train_movies]
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
                # Use pre-computed set for faster set operations
                similar_user_movies_set = user_to_movies_set[similar_user_id]
                # Set difference: movies in similar user's set but not in train set
                new_candidates = similar_user_movies_set - train_movies_set
                # Update counts
                candidate_movie_counts.update(new_candidates)

            if len(candidate_movie_counts) == 0:
                continue

            # Sort by frequency (most popular among similar users first)
            candidate_movies = [movie for movie, _ in candidate_movie_counts.most_common(candidate_pool_size)]

            # === RANKING STAGE ===
            # Rank candidates using pre-computed embeddings
            with torch.no_grad():  # Disable gradient computation for eval
                candidate_embs = self.movie_embeddings[candidate_movies]  # Direct lookup!

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

            # Update progress bar with current hitrate
            if total > 0:
                pbar.set_postfix({'hitrate': f'{hits/total:.4f}'})

        hitrate = hits / total if total > 0 else 0.0
        print(f"User-User CF HitRate@{k}: {hitrate:.4f} ({hitrate*100:.2f}%)")
        print(f"  Evaluated users: {total}")
        print(f"  Hits: {hits}")
        print(f"  Num similar users: {num_similar_users}")
        print(f"  Candidate pool size: {candidate_pool_size}")
        return hitrate


