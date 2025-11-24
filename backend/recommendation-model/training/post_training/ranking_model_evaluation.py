import polars as pl
import numpy as np
from shared.path_config import path_helper

class RankingModelEval: 
    def __init__(self, large_dataset: bool = False):
        paths = path_helper(large_dataset=large_dataset)

        movie_embeddings_path = paths.movie_embedding_path
        user_ratings_path = paths.pos_ratings_path
        
        # Read user ratings CSV
        user_df = pl.read_csv(user_ratings_path)

        # Load precomputed movie embeddings
        self.movie_embeddings = np.load(movie_embeddings_path)

        # Group by userId and aggregate movie_idx into lists
        grouped = user_df.group_by('userId').agg(pl.col('movie_idx'))

        # Convert to dict for easier access
        self.user_to_movies = {
            row['userId']: row['movie_idx']
            for row in grouped.iter_rows(named=True)
        }

    def leave_one_out_evaluation_user_to_movie(self, k: int = 10, min_ratings: int = 2):
        """
        Leave-one-out evaluation for personalized recommendations by computing sim from user to movie.

        For each user:
        1. Hold out their last rated movie as ground truth
        2. Average embeddings of their other rated movies
        3. Check if ground truth ranks in top-K

        Args:
            k: Top-K to check (e.g., 10 means check if movie is in top-10)
            min_ratings: Minimum number of ratings user needs (default: 2)

        Returns:
            float: HitRate@K
        """
        hits = 0
        total = 0

        print(f"\n=== Leave-One-Out Evaluation (HitRate@{k}) ===")
        print(f"Minimum ratings required: {min_ratings}")

        for user_id, rated_movies in self.user_to_movies.items():
            # Skip users with too few ratings
            if len(rated_movies) < min_ratings:
                continue

            # Hold out last movie as ground truth
            train_movies = rated_movies[:-1]
            test_movie = rated_movies[-1]

            # Generate user embedding (average of rated movies)
            train_embeddings = self.movie_embeddings[train_movies]  # (n_rated, 512)
            user_emb = train_embeddings.mean(axis=0)  # (512,)

            # Normalize for cosine similarity
            user_emb = user_emb / np.linalg.norm(user_emb)

            # Rank ALL movies by similarity
            scores = user_emb @ self.movie_embeddings.T  # (num_movies,)
            top_k_indices = np.argsort(scores)[-k:][::-1]

            # Check if ground truth is in top-K
            if test_movie in top_k_indices:
                hits += 1

            total += 1

        hitrate = hits / total if total > 0 else 0.0
        print(f"\nResults:")
        print(f"  Evaluated users: {total}")
        print(f"  Hits: {hits}")
        print(f"  HitRate@{k}: {hitrate:.4f} ({hitrate*100:.2f}%)")

        return hitrate

    def compare_to_random_baseline(self, k: int = 10):
        """
        Compare to random baseline.

        Random baseline = k / num_movies
        (Probability of randomly guessing the right movie in top-K)
        """
        num_movies = len(self.movie_embeddings)
        random_baseline = k / num_movies

        personalized_hitrate = self.leave_one_out_evaluation_user_to_movie(k=k)

        print(f"\n=== Baseline Comparison ===")
        print(f"Random baseline (HitRate@{k}): {random_baseline:.6f} ({random_baseline*100:.4f}%)")
        print(f"Personalized (HitRate@{k}): {personalized_hitrate:.4f} ({personalized_hitrate*100:.2f}%)")
        print(f"Improvement: {(personalized_hitrate / random_baseline):.2f}x better than random")

        return {
            'random': random_baseline,
            'personalized': personalized_hitrate,
            'improvement': personalized_hitrate / random_baseline
        }
