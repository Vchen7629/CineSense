import os
import polars as pl
import numpy as np
from utils.extract_features import extract_reranker_features_single
import time

class RerankerModelEval:
    def __init__(self,
                 model,
                 movie_embeddings,
                 user_embeddings,
                 movie_features_df,
                 user_features_df,
                 user_favorite_genres_df,
                 user_favorite_actor_director_df,
                 pos_ratings_df,
                 neg_ratings_df,
                 ) -> None:
        self.model = model
        self.movie_embeddings = movie_embeddings
        self.user_embeddings = user_embeddings
        self.pos_ratings_df = pos_ratings_df
        self.neg_ratings_df = neg_ratings_df

        self._precompute_lookups(
            user_features_df, 
            user_favorite_genres_df,
            user_favorite_actor_director_df, 
            movie_features_df
        )

    # Precompute user features as arrays and dicts, speeds up eval
    def _precompute_lookups(
        self, 
        user_features_df, 
        user_favorite_genres_df, 
        user_favorite_actor_director_df,
        movie_features_df
    ) -> None:
        user_features_sorted = user_features_df.sort('userId')
        max_user_id = user_features_sorted['userId'].max()

        # User features as arrays (sequential userId)
        self.user_rating_log = np.zeros(max_user_id + 1, dtype=np.float32)
        self.user_avg_rating = np.zeros(max_user_id + 1, dtype=np.float32)
        self.user_exists = np.zeros(max_user_id + 1, dtype=bool)

        user_ids = user_features_sorted['userId'].to_numpy()
        self.user_rating_log[user_ids] = user_features_sorted['user_rating_log'].to_numpy()
        self.user_avg_rating[user_ids] = user_features_sorted['user_avg_rating'].to_numpy()
        self.user_exists[user_ids] = True

        # precompute User features
        genres_data = user_favorite_genres_df.to_dict(as_series=False)
        self.user_fav_genres = {
            uid: genres_data['genres'][i]
            for i, uid in enumerate(genres_data['userId'])
        }

        cast_dir_data = user_favorite_actor_director_df.to_dict(as_series=False)
        self.user_fav_actors = {
            uid: cast_dir_data['top_50_actors'][i]
            for i, uid in enumerate(cast_dir_data['userId'])
        }
        self.user_fav_directors = {
            uid: cast_dir_data['top_10_directors'][i]
            for i, uid in enumerate(cast_dir_data['userId'])
        }

        # precompute movie features dict
        movie_data = movie_features_df.to_dict(as_series=False)
        self.movie_features_dict = {
            tmdb: {col: movie_data[col][i] for col in movie_data if col != 'tmdbId'}
            for i, tmdb in enumerate(movie_data['tmdbId'])
        }


    # leave-one-out HitRate@k eval for reranker
    # identifies if reranker can identify held-out pos among actual negatives
    # k: number of top recommendations to consider
    # num_negatives: number of samples per eval
    def hitrate(self, k: int = 10, num_negatives: int = 99):
        # get unique users who have both positives and negative ratings
        user_with_pos = set(self.pos_ratings_df['userId'].unique().to_list())
        user_with_neg = set(self.neg_ratings_df['userId'].unique().to_list())
        valid_users = user_with_pos & user_with_neg

        hits = 0
        total = 0

        for user_id in sorted(valid_users):
            user_hits, user_total = self._evaluate_user(
                user_id, num_negatives, k
            )

            hits += user_hits
            total += user_total

            if total > 0 and total % 100 == 0:
                print(f"  Processed {total} samples, current hitrate: {hits/total:.4f}")

        hitrate = hits / total if total > 0 else 0.0
        print(f"\nReranker HitRate@{k}: {hitrate:.4f} ({hitrate*100:.2f}%)")
        print(f"  Evaluated: {total} held-out positives")
        print(f"  Hits: {hits}")

        return hitrate

    def _get_user_data(self, user_id: int):
        if user_id >= len(self.user_embeddings) or user_id >= len(self.user_exists):
            return None
        if not self.user_exists[user_id]:
            return None

        user_emb = self.user_embeddings[user_id]
        user_features = {
            'user_rating_log': self.user_rating_log[user_id],
            'user_avg_rating': self.user_avg_rating[user_id]
        }
        user_fav_genres = {'genres': self.user_fav_genres.get(user_id, '')}
        user_fav_cast_dir = {
            'top_50_actors': self.user_fav_actors.get(user_id, ''),
            'top_10_directors': self.user_fav_directors.get(user_id, '')
        }

        return user_emb, user_features, user_fav_genres, user_fav_cast_dir

    def _evaluate_user(self, user_id: int, num_negatives: int, k: int):
        # get user's positive and negative samples
        user_positives = self.pos_ratings_df.filter(pl.col("userId") == user_id)
        user_negatives = self.neg_ratings_df.filter(pl.col("userId") == user_id)

        if len(user_negatives) < num_negatives:
            return 0, 0

        user_data = self._get_user_data(user_id)
        if user_data is None:
            return 0, 0

        user_emb, user_features, user_fav_genres, user_fav_cast_dir = user_data

        # Get arrays
        pos_idx = user_positives['movie_idx'].to_numpy()
        pos_tmdb = user_positives['tmdbId'].to_numpy()
        neg_idx = user_negatives['movie_idx'].to_numpy()
        neg_tmdb = user_negatives['tmdbId'].to_numpy()

        hits = 0
        total = 0

        # evaluate each positive (leave-one-out)
        for held_out_idx, held_out_tmdb in zip(pos_idx, pos_tmdb):
            # sample random negatives
            sample_indices = np.random.choice(len(neg_idx), num_negatives, replace=False)

            # combine held out and sampled negatives
            candidate_idx = np.concatenate([[held_out_idx], neg_idx[sample_indices]])
            candidate_tmdb = np.concatenate([[held_out_tmdb], neg_tmdb[sample_indices]])

            # extract feature
            X = extract_reranker_features_single(
                candidate_idx, candidate_tmdb, user_emb, user_features,
                user_fav_genres, user_fav_cast_dir, self.movie_embeddings, self.movie_features_dict
            )


            if X is None or len(X) < 2:
                continue

            # predict and check if held-out is in top-k
            scores = self.model.predict(X)
            if 0 in np.argsort(scores)[::-1][:k]:
                hits += 1
            total += 1

        return hits, total
