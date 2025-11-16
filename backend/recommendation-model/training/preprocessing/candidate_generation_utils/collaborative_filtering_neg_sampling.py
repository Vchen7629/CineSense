import os
import polars as pl
import numpy as np
import time
import csv

current_dir = os.path.dirname(__file__)

def collaborative_filtering_negative_sampling(num_sets: int = 10, num_negatives: int = 64, large_dataset: bool = False):
    if large_dataset:
        negative_output_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-collaborative-negatives.csv")
        user_csv_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-output.csv")
    else:
        negative_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-collaborative-negatives.csv")
        user_csv_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-output.csv")

    user_df = pl.read_csv(user_csv_path)

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
            
            # find negative pool for this user
            neg_candidates = all_movies[~np.isin(all_movies, list(pos_movies))]
            total_negatives_needed = num_negatives * num_sets

            # Sample negatives for all sets at once
            if len(neg_candidates) >= total_negatives_needed:
                all_sampled = np.random.choice(neg_candidates, size=total_negatives_needed, replace=False)
            else:
                # handling edge case where user rated almost everything
                all_sampled = np.pad(neg_candidates, (0, total_negatives_needed - len(neg_candidates)), mode='wrap')

            # build row: userId + all negatives
            row = [user] + all_sampled.tolist() 
            writer.writerow(row)

    file_size_mb = os.path.getsize(negative_output_path) / (1024 * 1024)
    print(f"Done! File size: {file_size_mb:.1f} MB")