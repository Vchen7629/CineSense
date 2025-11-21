import lightgbm as lgb
import numpy as np
import os
from typing import List, Any

class Reranker:
    def __init__(self, production: bool = False):
        
        current_dir = os.path.dirname(__file__)

        if not production:
            model_file = os.path.join(current_dir, "..", "files_small", "reranker-model.txt")
        else:
            model_file = "todo: load from s3"

        self.model = lgb.Booster(model_file=model_file)
    
    def _compute_feature_overlap(self, user_features: List[str], movie_features: List[str]) -> np.ndarray:
        """Compute between user and movie feature lists"""
        user_set = set(user_features) if user_features else set()

        overlaps = []
        for movie_feature in movie_features:
            movie_set = set(movie_feature) if movie_features else set()
            overlaps.append(len(user_set & movie_set))
        
        return np.array(overlaps, dtype=np.float32)


    def rerank_movies(self, user_metadata, candidate_movies: List[Any]):
        
        features = []

        genre_overlap = self._compute_feature_overlap(
            user_metadata['top_3_genres'],
            [candidate.genres for candidate in candidate_movies]
        )
            
        actor_overlap = self._compute_feature_overlap(
            user_metadata['top_50_actors'],
            [candidate.actors for candidate in candidate_movies]
        )

        director_overlap = self._compute_feature_overlap(
            user_metadata['top_10_directors'],
            [candidate.directors for candidate in candidate_movies]
        )
        
        for candidate in candidate_movies:
            # compute collab_score (cosine similarity between user and movie embeddings)
            collab_score = user_metadata['embedding']

            recency_score = (1 - ((2025 - candidate.release_date) / 50))
            recency_user_avg = recency_score * user_metadata['avg_rating']

            feature_row = [
                collab_score,
                candidate.rating_count_log,
                candidate.avg_rating,
                candidate.tmdb_avg_rating,
                candidate.tmdb_vote_log,
                candidate.tmdb_popularity,
                recency_score,
                recency_user_avg,
                user_metadata['rating_log'],
                user_metadata['avg_rating'],
                genre_overlap,
                actor_overlap,
                director_overlap
            ]

            features.append(feature_row)
        
        X = np.array(features, dtype=np.float32)
        
        # Predict with LightGBM reranker model
        scores = self.model.predict(X)

        # rerank candidates by score
        top_10_movies = sorted(zip(candidate_movies, scores), key=lambda x: x[1], reverse=True)[:10]

        return top_10_movies