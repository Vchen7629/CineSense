import os
import polars as pl
import numpy as np
import time
import csv

current_dir = os.path.dirname(__file__)

def collaborative_filtering_negative_sampling(
    num_sets: int = 10, 
    num_negatives: int = 64, 
    hard_neg_ratio: float = 0.5,
    large_dataset: bool = False
) -> None:
    if large_dataset:
        negative_output_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-collaborative-negatives.csv")
        positive_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-positive-ratings.csv")
        negative_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-negative-ratings.csv")
    else:
        negative_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-collaborative-negatives.csv")
        positive_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-positive-ratings.csv")
        negative_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-negative-ratings.csv")

    pos_df = pl.read_csv(positive_ratings_path)
    neg_df = pl.read_csv(negative_ratings_path)

    # get all unique movie ids
    all_movies = pl.concat([
        pos_df['movie_idx'].unique(), 
        neg_df['movie_idx'].unique()
    ]).unique().to_numpy()
    
    # group by user to find their positive movies
    user_pos_groups = pos_df.group_by('userId').agg(pl.col('movie_idx'))
    user_to_pos_movies = {row['userId']: set(row['movie_idx']) for row in user_pos_groups.iter_rows(named=True)}

    # group by user to find their negative movies
    user_neg_groups = neg_df.group_by('userId').agg(pl.col('movie_idx'))
    user_to_neg_movies = {row['userId']: set(row['movie_idx']) for row in user_neg_groups.iter_rows(named=True)}

    # creating column names
    col_names = ['userId']
    for set_id in range(num_sets):
        for neg_idx in range(num_negatives):
            col_names.append( f"neg_set{set_id}_item{neg_idx}")

    # Sort users to ensure consistent ordering
    num_users = len(user_to_pos_movies)
    print(f"Sampling negatives for {num_users} users across {num_sets} sets...")
    print(f"Negative split: {hard_neg_ratio*100:.0f}% hard, {(1-hard_neg_ratio)*100:.0f}% random")
    print(f"Writing to {negative_output_path}...")
    start_time = time.perf_counter()

    # calculate split sizes for 50% hard 50% random
    num_hard = int(num_negatives * hard_neg_ratio)
    num_random = num_negatives - num_hard

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

            # find all unrated movies for the user that are neither positive or negative
            rated_movies = pos_movies | neg_movies
            unrated_movies = all_movies[~np.isin(all_movies, list(rated_movies))] 
            
            # Sample negatives for all sets at once
            all_sampled = []
            for _ in range(num_sets):
                # hard negatives: user's rated movies that are low rated (<= 3.5)
                if len(neg_movies) >= num_hard:
                    hard_sample = np.random.choice(list(neg_movies), num_hard, replace=False)
                    num_random_adjust = num_random
                else:
                    # not enough hard negatives, sample what we have
                    hard_sample = np.array(list(neg_movies))
                    num_random_adjust = num_negatives - len(hard_sample)

                # random negatives: any movie that the user didnt rate
                if len(unrated_movies) >= num_random_adjust:
                    random_sample = np.random.choice(unrated_movies, num_random_adjust, replace=False)
                else:
                    # handling edge case where user rated almost everything
                    random_sample = np.pad(unrated_movies, (0, num_random_adjust - len(unrated_movies)), mode='wrap')

                # combine and shuffle
                set_negatives = np.concatenate([hard_sample, random_sample])
                np.random.shuffle(set_negatives)
                all_sampled.extend(set_negatives.tolist())

            # build row: userId + all negatives
            row = [user] + all_sampled 
            writer.writerow(row)

    file_size_mb = os.path.getsize(negative_output_path) / (1024 * 1024)
    print(f"Done! File size: {file_size_mb:.1f} MB")