import os
import polars as pl

# normalize the ratings values for user rated movies in training dataset to match what production
# will have. training dataset is 0.5 -> 5.0 while production is 1 -> 5
def normalize_ratings(large_dataset: bool = False) -> None:
    current_dir = os.path.dirname(__file__)

    if large_dataset:
        ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest", "ratings.csv")
    else:
        ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest-small", "ratings.csv")
    
    ratings_df = pl.read_csv(ratings_path)

    rounded_ratings_df = (
        ratings_df
            .with_columns(
                pl.col("rating").ceil().cast(pl.Int8).alias("rating")
            )
    )

    rounded_ratings_df.write_csv(ratings_path)