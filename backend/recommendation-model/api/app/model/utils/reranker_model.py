import lightgbm as lgb
import numpy as np
import os
from typing import List, Any
from middleware.config import settings

class Reranker:
    def __init__(self):
        
        self._load_model_file()

        self.model = lgb.Booster(model_file=self.reranker_model_path)

    def _load_model_file(self):
        reranker_model_path = settings.reranker_model_path

        # Download from S3 if needed
        if reranker_model_path.startswith("s3://"):
            pass

        self.reranker_model_path = reranker_model_path
    
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
            [candidate['genres'] for candidate in candidate_movies]
        )

        actor_overlap = self._compute_feature_overlap(
            user_metadata['top_50_actors'],
            [candidate['actors'] for candidate in candidate_movies]
        )

        director_overlap = self._compute_feature_overlap(
            user_metadata['top_10_directors'],
            [candidate['directors'] for candidate in candidate_movies]
        )

        # Parse user embedding from pgvector string format "[x,y,z,...]" to numpy array
        user_emb_str = user_metadata['embedding'].strip('[]')
        user_emb = np.fromstring(user_emb_str, sep=',', dtype=np.float32)

        for i, candidate in enumerate(candidate_movies):
            # compute collab_score (cosine similarity between user and movie embeddings)
            # Parse movie embedding from pgvector string format
            movie_emb_str = candidate['movie_emb'].strip('[]')
            movie_emb = np.fromstring(movie_emb_str, sep=',', dtype=np.float32)
            collab_score = np.dot(user_emb, movie_emb) / (
                np.linalg.norm(user_emb) * np.linalg.norm(movie_emb) + 1e-8
            )

            recency_score = (1 - ((2025 - candidate['release_date']) / 50))
            recency_user_avg = recency_score * user_metadata['avg_rating']

            feature_row = [
                collab_score,
                candidate['movie_rating_log'],
                candidate['movie_avg_rating'],
                candidate['tmdb_vote_avg'],
                candidate['tmdb_vote_log'],
                candidate['tmdb_popularity'],
                recency_score,
                recency_user_avg,
                user_metadata['rating_log'],
                user_metadata['avg_rating'],
                genre_overlap[i],
                actor_overlap[i],
                director_overlap[i]
            ]

            features.append(feature_row)
        
        X = np.array(features, dtype=np.float32)
        
        # Predict with LightGBM reranker model
        scores = self.model.predict(X)

        # rerank candidates by score
        top_10_movies = sorted(zip(candidate_movies, scores), key=lambda x: x[1], reverse=True)[:10]

        # Remove movie embeddings from response and format results
        results = []
        for movie, score in top_10_movies:
            movie_clean = {k: v for k, v in movie.items() if k != 'movie_emb'}
            movie_clean['score'] = float(score)
            results.append(movie_clean)

        return results