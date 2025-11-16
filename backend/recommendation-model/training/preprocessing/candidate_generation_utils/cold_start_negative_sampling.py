import os
import polars as pl
from shared.load_genres import load_genre_mappings
from shared.split_hard_random_candidates import split_hard_random_candidates
import time
import csv
import numpy as np

current_dir = os.path.dirname(__file__)

# This preprocessing step creates mixed negative samples with 64 negatives per user
# mixed negatives = 80% hard (from user's top-3 genres) + 20% random (any genre)
# Hard negatives teach the model to distinguish within preferred genres (actor/director preferences)
# Creates 10 sets so model can cycle through without overfitting
def cold_start_negative_sampling(num_sets: int = 10, num_negatives: int = 64, genre_ratio: float = 0.8, large_dataset: bool = False):
    if large_dataset:
        negative_output_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-cold-start-negatives.csv")
        user_csv_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-output.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output", "movie-metadata.csv")
        user_genre_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-top3-genres.csv")
    else:
        negative_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-cold-start-negatives.csv")
        user_csv_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-output.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "movie-metadata.csv")
        user_genre_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-top3-genres.csv")

    user_df = pl.read_csv(user_csv_path)

    user_to_genres, movie_to_genres = load_genre_mappings(user_genre_path, movie_metadata_path)

    # get all unique movie ids
    all_movies = user_df['movie_idx'].unique().to_numpy()
    
    # group by user to find their positive movies
    user_groups = user_df.group_by('userId').agg(pl.col('movie_idx'))
    user_to_movies = {row['userId']: set(row['movie_idx']) for row in user_groups.iter_rows(named=True)}

    # creating column names
    col_names = ['userId']
    for set_id in range(num_sets):
        for neg_idx in range(num_negatives):
            col_names.append( f"neg_set{set_id}_item{neg_idx}")

    # Sort users to ensure consistent ordering
    num_users = len(user_to_movies)
    print(f"Sampling negatives for {num_users} users across {num_sets} sets...")
    print(f"Writing to {negative_output_path}...")
    start_time = time.perf_counter()

    # write to csv
    with open(negative_output_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(col_names)

        for idx, user in enumerate(sorted(user_to_movies.keys())):
            if (idx + 1) % 10000 == 0:
                elapsed = time.perf_counter() - start_time
                print(f"{idx + 1}/{num_users} users ({elapsed:.1f}s, {(idx + 1)/elapsed:.0f} users/s)")

            pos_movies = user_to_movies[user]
            user_genres = user_to_genres.get(user, set())

            # Find all unrated movies
            unrated_movies = all_movies[~np.isin(all_movies, list(pos_movies))]

            # Sample negatives for all sets at once
            all_sampled = []
            for _ in range(num_sets):
                # Split into hard and random candidates
                genre_candidates, num_genre, num_random = split_hard_random_candidates(
                    unrated_movies, movie_to_genres, user_genres, num_negatives, genre_ratio
                )

                # Sample hard negatives (from user's top-3 genres)
                if len(genre_candidates) >= num_genre:
                    genre_sample = np.random.choice(genre_candidates, num_genre, replace=False)
                else:
                    genre_sample = genre_candidates
                    num_random = num_negatives - len(genre_sample)

                # Sample random negatives (excluding genre samples)
                non_genre_candidates = np.setdiff1d(unrated_movies, genre_sample)
                if len(non_genre_candidates) >= num_random:
                    random_sample = np.random.choice(non_genre_candidates, num_random, replace=False)
                else:
                    random_sample = non_genre_candidates[:num_random]

                # Combine and shuffle
                set_negatives = np.concatenate([genre_sample, random_sample])
                np.random.shuffle(set_negatives)
                all_sampled.extend(set_negatives.tolist())

            # build row: userId + all negatives
            row = [user] + all_sampled
            writer.writerow(row)

    file_size_mb = os.path.getsize(negative_output_path) / (1024 * 1024)
    print(f"Done! File size: {file_size_mb:.1f} MB")