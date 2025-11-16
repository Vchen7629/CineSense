import os
import pandas as pd

current_dir = os.path.dirname(__file__)

# creates a new csv (user-output.csv) with only ratings that are the positive (>3.0) in the user dataset
def filter_positive_ratings(large_dataset: bool = False) -> None:
    if large_dataset:
        user_csv_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-output.csv")
        ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest", "ratings.csv")
    else:
        user_csv_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-output.csv")
        ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest-small", "ratings.csv")

    ratings_df = pd.read_csv(ratings_path)

    # filter original dataset for positive ratings only (greater than 3.0 rating)
    positive_ratings = ratings_df["rating"] > 3.0

    # Create a new df with only the positive ratings users and no timestamp column
    filtered_df = ratings_df[positive_ratings].drop(columns=["timestamp"])

    # remove gaps from filtered users
    unique_users = sorted(filtered_df['userId'].unique())
    user_id_to_idx = {user_id: idx for idx, user_id in enumerate(unique_users)}
    filtered_df["userId"] = filtered_df["userId"].map(user_id_to_idx)

    # write the processed dataset to a csv
    filtered_df.to_csv(user_csv_path, index=False)