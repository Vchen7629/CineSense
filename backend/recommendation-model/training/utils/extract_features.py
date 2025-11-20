import polars as pl
import numpy as np
from utils.compute_feature_overlap import compute_set_overlap

# extract all features for a batch of (user, movie pair) from joined Dataframe
# used in training
def extract_reranker_features_batch(user_emb, movie_emb, ratings_with_features: pl.DataFrame) -> np.ndarray:
    # collaborative filtering score (cosine similarity)
    user_ids = ratings_with_features['userId'].to_numpy()
    movie_indicies = ratings_with_features['movie_idx'].to_numpy()

    user_embs = user_emb[user_ids]
    movie_embs = movie_emb[movie_indicies]

    collab_score = np.sum(user_embs * movie_embs, axis=1) / (
        np.linalg.norm(user_embs, axis=1) * np.linalg.norm(movie_embs, axis=1) + 1e-8
    )

    # movie popularity features
    movie_rating_log = ratings_with_features['movie_rating_log'].fill_null(0.0).to_numpy()
    movie_avg_rating = ratings_with_features['movie_avg_rating'].fill_null(0.0).to_numpy()

    # TMDB features
    tmdb_vote_avg = ratings_with_features['tmdb_vote_average'].fill_null(0.0).to_numpy()
    tmdb_vote_log = ratings_with_features['tmdb_vote_count_log'].fill_null(0.0).to_numpy()
    tmdb_popularity = ratings_with_features['tmdb_popularity'].fill_null(0.0).to_numpy()

    # recency score
    recency_score = ratings_with_features['recency_score'].fill_null(0.0).to_numpy()

    # user activity features
    user_rating_log = ratings_with_features['user_rating_log'].fill_null(0.0).to_numpy()
    user_avg_rating = ratings_with_features['user_avg_rating'].fill_null(0.0).to_numpy()

    # feature for expressing if users who rate highly prefer recent movies
    recency_user_avg = recency_score * user_avg_rating

    # rating gap feature to see if user tends to rate higher or lower than average movie rating from all users in dataset
    rating_gap = user_avg_rating - movie_avg_rating

    # rating gap feature to check gap between tmdb ratings and dataset rating
    tmdb_internal_gap = tmdb_vote_avg - movie_avg_rating

    # interaction features
    genre_overlaps = compute_set_overlap( # raw count of overlaps
        ratings_with_features['genres'].fill_null('').to_list(),
        ratings_with_features['genres_normalized'].fill_null('').to_list()
    )

    actor_overlaps = compute_set_overlap(
        ratings_with_features['top_50_actors'].fill_null('').to_list(),
        ratings_with_features['cast_normalized'].fill_null('').to_list()
    )

    director_overlaps = compute_set_overlap(
        ratings_with_features['top_10_directors'].fill_null('').to_list(),
        ratings_with_features['director'].fill_null('').to_list()
    )

    # normalize overlap for genres by total genres user likes and total genres the movie has
    num_user_genres = ratings_with_features['num_user_genres'].fill_null(0).to_numpy()
    num_movie_genres = ratings_with_features['num_genres'].fill_null(0).to_numpy()

    genre_overlaps_normalized = genre_overlaps / (np.sqrt(num_user_genres * num_movie_genres) + 1e-8)

    # normalize overlap for actors by total actors user likes and total actors the movie has
    num_user_actors = ratings_with_features['num_user_actors'].fill_null(0).to_numpy()
    num_movie_actors = ratings_with_features['num_cast'].fill_null(0).to_numpy()

    actor_overlaps_normalized = actor_overlaps / (np.sqrt(num_user_actors * num_movie_actors) + 1e-8)

    # normalize overlap for director by total director user likes and total director the movie has
    num_user_director = ratings_with_features['num_user_director'].fill_null(0).to_numpy()
    num_movie_director = ratings_with_features['num_directors'].fill_null(0).to_numpy()

    director_overlaps_normalized = director_overlaps / (np.sqrt(num_user_director * num_movie_director) + 1e-8)

    # features to boost true positives for overlaps

    # high collaborative similarity with the user and also overlaps with alot of the user's top 3 genre
    collab_score_genre_overlap = collab_score * genre_overlaps_normalized

    # high collaborative similarity with the user and also overlaps with alot of the user's top 50 actors
    collab_score_actor_overlap = collab_score * actor_overlaps_normalized

    # high collaborative similarity with the user and also overlaps with alot of the user's top 10 directors
    collab_score_director_overlap = collab_score * director_overlaps_normalized

    # stack all features
    return np.column_stack([
        collab_score,
        movie_rating_log,
        movie_avg_rating,
        tmdb_vote_avg,
        tmdb_vote_log,
        tmdb_popularity,
        recency_score,
        recency_user_avg,
        user_rating_log,
        user_avg_rating,
        #rating_gap,
        #tmdb_internal_gap,
        genre_overlaps,
        actor_overlaps,
        director_overlaps,
        #genre_overlaps_normalized,
        #actor_overlaps_normalized,
        #director_overlaps_normalized,
        #collab_score_genre_overlap,
        #collab_score_actor_overlap,
        #collab_score_director_overlap,
    ])

# extract features for a single (user, movie) pair, used for eval where pairs are created dynamically
def extract_reranker_features_single(
    candidate_idx,
    candidate_tmdb,
    user_embs,
    user_features,
    user_fav_genres,
    user_fav_cast_dir,
    movie_embeddings,
    movie_features_dict
):
    # Get embeddings
    movie_embs = movie_embeddings[candidate_idx]

    valid_indices = []
    movie_features_list = []
    for i, tmdb in enumerate(candidate_tmdb):
        if tmdb in movie_features_dict:
            valid_indices.append(i)
            movie_features_list.append(movie_features_dict[tmdb])

    if not valid_indices:
        return None

    movie_embs = movie_embs[valid_indices]
    N = len(valid_indices)
    
    # collaborative filtering score
    user_embs_batch = np.tile(user_embs, (N, 1))
    collab_score = np.sum(user_embs_batch * movie_embs, axis=1) / (
        np.linalg.norm(user_embs_batch, axis=1) * np.linalg.norm(movie_embs, axis=1) + 1e-8
    )

    # movie popularity features
    movie_rating_log = np.array([m['movie_rating_log'] for m in movie_features_list])
    movie_avg_rating = np.array([m['movie_avg_rating'] for m in movie_features_list])

    # tmdb movie detail features
    tmdb_vote_avg = np.array([m['tmdb_vote_average'] for m in movie_features_list])
    tmdb_vote_log = np.array([m['tmdb_vote_count_log'] for m in movie_features_list])
    tmdb_popularity = np.array([m['tmdb_popularity'] for m in movie_features_list])

    # recency score
    recency_score = np.array([m['recency_score'] for m in movie_features_list])

    # user activity features
    user_rating_log = np.full(N, user_features.get('user_rating_log', 0.0))
    user_avg_rating = np.full(N, user_features.get('user_avg_rating', 0.0))

    # feature for expressing if users who rate highly prefer recent movies
    recency_user_avg = recency_score * user_avg_rating

    # rating gap feature to see if user tends to rate higher or lower than average movie rating
    rating_gap = user_avg_rating - movie_avg_rating

    # rating gap feature to check gap between tmdb ratings and dataset rating
    tmdb_internal_gap = tmdb_vote_avg - movie_avg_rating

    # interaction features
    user_genres_str = user_fav_genres.get('genres', '') if user_fav_genres else ''
    user_actors_str = user_fav_cast_dir.get('top_50_actors', '') if user_fav_cast_dir else ''
    user_directors_str = user_fav_cast_dir.get('top_10_directors', '') if user_fav_cast_dir else ''

    user_genres_list = [user_genres_str] * N
    user_actors_list = [user_actors_str] * N
    user_directors_list = [user_directors_str] * N

    movie_genres_list = np.array([m['genres_normalized'] for m in movie_features_list])
    movie_cast_list = np.array([m['cast_normalized'] for m in movie_features_list])
    movie_directors_list = np.array([m['director'] for m in movie_features_list])

    genre_overlaps = compute_set_overlap(user_genres_list, movie_genres_list)
    actor_overlaps = compute_set_overlap(user_actors_list, movie_cast_list)
    director_overlaps = compute_set_overlap(user_directors_list, movie_directors_list)

    # Get normalization counts from movie features
    num_user_genres = user_fav_genres.get('num_user_genres', 0) if user_fav_genres else 0
    num_user_actors = user_fav_cast_dir.get('num_user_actors', 0) if user_fav_cast_dir else 0
    num_user_directors = user_fav_cast_dir.get('num_user_director', 0) if user_fav_cast_dir else 0

    num_movie_genres = np.array([m.get('num_genres', 0) for m in movie_features_list])
    num_movie_actors = np.array([m.get('num_cast', 0) for m in movie_features_list])
    num_movie_directors = np.array([m.get('num_directors', 0) for m in movie_features_list])

    # Normalize overlaps
    genre_overlaps_normalized = genre_overlaps / (np.sqrt(num_user_genres * num_movie_genres) + 1e-8)
    actor_overlaps_normalized = actor_overlaps / (np.sqrt(num_user_actors * num_movie_actors) + 1e-8)
    director_overlaps_normalized = director_overlaps / (np.sqrt(num_user_directors * num_movie_directors) + 1e-8)

    # Interaction features
    collab_score_genre_overlap = collab_score * genre_overlaps_normalized
    collab_score_actor_overlap = collab_score * actor_overlaps_normalized
    collab_score_director_overlap = collab_score * director_overlaps_normalized

    return np.column_stack([
        collab_score,
        movie_rating_log,
        movie_avg_rating,
        tmdb_vote_avg,
        tmdb_vote_log,
        tmdb_popularity,
        recency_score,
        recency_user_avg,
        user_rating_log,
        user_avg_rating,
        #rating_gap,
        #tmdb_internal_gap,
        genre_overlaps,
        actor_overlaps,
        director_overlaps,
        #genre_overlaps_normalized,
        #actor_overlaps_normalized,
        #director_overlaps_normalized,
        #collab_score_genre_overlap,
        #collab_score_actor_overlap,
        #collab_score_director_overlap,
    ]).astype(np.float32)