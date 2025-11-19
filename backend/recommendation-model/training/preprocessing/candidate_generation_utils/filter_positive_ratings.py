import os
import polars as pl

current_dir = os.path.dirname(__file__)

# creates a new csv (user-output.csv) with only ratings that are the positive (>3) in the user dataset
def filter_positive_ratings(large_dataset: bool = False) -> None:
    if large_dataset:
        all_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest", "ratings.csv")
        movie_links_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest", "links.csv")
        positive_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-positive-ratings.csv")
        negative_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-negative-ratings.csv")
    else:
        all_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest-small", "ratings.csv")
        movie_links_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest-small", "links.csv")
        positive_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-positive-ratings.csv")
        negative_ratings_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-negative-ratings.csv")

    ratings_df = pl.read_csv(all_ratings_path)
    links_df = pl.read_csv(movie_links_path)

    # split into positive (>=4) and negative (<=3) ratings
    positive_df = ratings_df.filter(pl.col("rating") >= 4).drop("timestamp")
    negative_df = ratings_df.filter(pl.col("rating") <= 3).drop("timestamp")

    # remove gaps from filtered users - only users who have both positive and negative ratings
    users_with_positives = set(positive_df['userId'].unique().to_list())
    users_with_negatives = set(negative_df['userId'].unique().to_list())
    users_with_both = sorted(users_with_positives & users_with_negatives)

    print(f"Users with pos ratings: {len(users_with_positives)}")
    print(f"Users with neg ratings: {len(users_with_negatives)}")
    print(f"Users with both {len(users_with_both)}")

    # create user ID mapping
    user_id_to_idx = {user_id: idx for idx, user_id in enumerate(users_with_both)}

    # filter to only users with both types and remap IDs
    positive_df = positive_df.filter(pl.col("userId").is_in(users_with_both))
    negative_df = negative_df.filter(pl.col("userId").is_in(users_with_both))

    positive_df = positive_df.with_columns(
       pl.col("userId").replace(user_id_to_idx, default=None).alias("userId")
    )
    negative_df = negative_df.with_columns(
       pl.col("userId").replace(user_id_to_idx, default=None).alias("userId")
    )
    
    # add tmdb id column corresponding to each movie
    positive_df = positive_df.join(links_df.select(["movieId", "tmdbId"]), on="movieId", how="left")
    negative_df = negative_df.join(links_df.select(["movieId", "tmdbId"]), on="movieId", how="left")

    # write the processed datasets to a csv
    positive_df.write_csv(positive_ratings_path)
    negative_df.write_csv(negative_ratings_path)