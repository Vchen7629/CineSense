import os
import polars as pl
from shared.load_genres import load_genre_mappings
from shared.split_hard_random_candidates import split_hard_random_candidates
import time
import csv
import numpy as np

current_dir = os.path.dirname(__file__)

# This preprocessing step creates mixed negative samples with 64 negatives per user
# For cold start: 80% genre-based (from user's top-3 genres) + 20% random (any genre)
# No hard negatives since we're simulating cold start where we only know genre preferences
# Genre-based negatives are harder (same genre, different quality)
# Creates 10 sets so model can cycle through without overfitting
def cold_start_negative_sampling(
    num_sets: int = 10,
    num_negatives: int = 64,
    genre_ratio: float = 0.8,
    large_dataset: bool = False
) -> None:
    if large_dataset:
        negative_output_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-cold-start-negatives.csv")
        positive_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-positive-ratings.csv")
        negative_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-negative-ratings.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output", "movie-metadata.csv")
        user_genre_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-top3-genres.csv")
    else:
        negative_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-cold-start-negatives.csv")
        positive_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-positive-ratings.csv")
        negative_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-negative-ratings.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "movie-metadata.csv")
        user_genre_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-top3-genres.csv")

    pos_df = pl.read_csv(positive_ratings_path)
    neg_df = pl.read_csv(negative_ratings_path)

    user_to_genres, movie_to_genres = load_genre_mappings(user_genre_path, movie_metadata_path)

    # get all unique movie ids
    all_movies = pl.concat([
        pos_df['movie_idx'].unique(), 
        neg_df['movie_idx'].unique()
    ]).unique().to_numpy()
    
    # group by user to find their positive movies
    pos_groups = pos_df.group_by('userId').agg(pl.col('movie_idx'))
    user_to_pos_movies = {row['userId']: set(row['movie_idx']) for row in pos_groups.iter_rows(named=True)}

    # group by user to find their negative movies
    neg_groups = neg_df.group_by('userId').agg(pl.col('movie_idx'))
    user_to_neg_movies = {row['userId']: set(row['movie_idx']) for row in neg_groups.iter_rows(named=True)}

    # creating column names
    col_names = ['userId']
    for set_id in range(num_sets):
        for neg_idx in range(num_negatives):
            col_names.append(f"neg_set{set_id}_item{neg_idx}")

    # Sort users to ensure consistent ordering
    num_users = len(user_to_pos_movies)
    print(f"Negative split: {genre_ratio*100:.0f}% genre, {(1-genre_ratio)*100:.0f}% random")
    print(f"Writing to {negative_output_path}...")
    start_time = time.perf_counter()

    # calculate split sizes for 80% genre, 20% random
    num_genre = int(num_negatives * genre_ratio)
    num_random = num_negatives - num_genre

    # write to csv
    with open(negative_output_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(col_names)

        for idx, user in enumerate(sorted(user_to_pos_movies.keys())):
            if (idx + 1) % 10000 == 0:
                elapsed = time.perf_counter() - start_time
                print(f"{idx + 1}/{num_users} users ({elapsed:.1f}s, {(idx + 1)/elapsed:.0f} users/s)")

            pos_movies = user_to_pos_movies[user]
            neg_movies = user_to_neg_movies.get(user, set())
            user_genres = user_to_genres.get(user, set())

            # Find all unrated movies (neither positive nor negative)
            rated_movies = pos_movies | neg_movies # set union operator to combine both sets
            unrated_movies = all_movies[~np.isin(all_movies, list(rated_movies))]

            # Sample negatives for all sets at once
            all_sampled = []
            for _ in range(num_sets):
                # Genre-based negatives: movies that have genres a part of user's top-3 genres that they haven't rated
                genre_candidates = np.array([
                    m for m in unrated_movies
                    if movie_to_genres.get(m, set()) & user_genres
                ])

                if len(genre_candidates) >= num_genre:
                    genre_sample = np.random.choice(genre_candidates, num_genre, replace=False)
                    num_random_adjust = num_random
                else:
                    # Not enough genre candidates, use what we have and fill rest with random
                    genre_sample = genre_candidates
                    num_random_adjust = num_negatives - len(genre_sample)

                # Sample random negatives: any movie the user hasn't rated excluding genre samples
                random_candidates = np.setdiff1d(unrated_movies, genre_sample)

                if len(random_candidates) >= num_random_adjust:
                    random_sample = np.random.choice(random_candidates, num_random_adjust, replace=False)
                elif len(random_candidates) > 0:
                    # Not enough unique candidates, use replacement sampling
                    random_sample = np.random.choice(random_candidates, num_random_adjust, replace=True)
                else:
                    # No random candidates available, sample from unrated movies with replacement
                    random_sample = np.random.choice(unrated_movies, num_random_adjust, replace=True)

                # Combine and shuffle
                set_negatives = np.concatenate([genre_sample, random_sample])
                np.random.shuffle(set_negatives)

                # Safety check: ensure exactly num_negatives items
                if len(set_negatives) < num_negatives:
                    # This shouldn't happen with the logic above, but just in case
                    padding = np.random.choice(unrated_movies, num_negatives - len(set_negatives), replace=True)
                    set_negatives = np.concatenate([set_negatives, padding])

                all_sampled.extend(set_negatives.tolist())

            # build row: userId + all negatives
            row = [user] + all_sampled
            writer.writerow(row)

    file_size_mb = os.path.getsize(negative_output_path) / (1024 * 1024)
    print(f"Done! File size: {file_size_mb:.1f} MB")