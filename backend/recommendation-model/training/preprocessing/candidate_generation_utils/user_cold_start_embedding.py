import os
import polars as pl
from sklearn.preprocessing import MultiLabelBinarizer
import numpy as np
import joblib

current_dir = os.path.dirname(__file__)

# Extracts the User's top 3 preferred genres and creates npy file with an mlb embedding
# this is only used during training for the cold start model
def create_user_preferred_genres_embedding(large_dataset: bool = False) -> None:
    if large_dataset:
        genre_output = os.path.join(current_dir, "..", "..", "datasets", "output", "preferred-genres.npy")
        user_csv_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-output.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output", "movie-metadata.csv")
        user_genre_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-top3-genres.csv")
        genre_mlb_path = os.path.join(current_dir, "..", "..", "datasets", "output", "genre_mlb.joblib")
    else:
        genre_output = os.path.join(current_dir, "..", "..", "datasets", "output-small", "preferred-genres.npy")
        user_csv_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-output.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "movie-metadata.csv")
        user_genre_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-top3-genres.csv")
        genre_mlb_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "genre_mlb.joblib")

    user_df = pl.read_csv(user_csv_path)
    movie_df = pl.read_csv(movie_metadata_path)
    genre_mlb = joblib.load(genre_mlb_path)
    
    # group by user to find movie_idxs
    user_groups = user_df.group_by('userId').agg(pl.col('movie_idx')).sort("userId")
    # explode to convert the list of movie_idx [0, 2,...] into seperate rows
    user_groups_exploded = user_groups.explode("movie_idx")

    # create a new df containing rows with userId, movie_idx, movie_Id, title, and genres
    user_movies_df = (
        user_groups_exploded.join(movie_df, left_on=pl.col('movie_idx'), right_on=pl.col('movie_idx'), how='left')
        .drop(["movieId", "movie_idx", "title"]) # remove these columns since its not necessary
    )

    genres_df = (
        user_movies_df
        .with_columns(pl.col('genres_normalized').str.split("|")) # split into list
        .explode(pl.col("genres_normalized")) # split the list of genres into seperate rows
        .group_by(["userId", "genres_normalized"]) # create unique userId, genre pairs
        .agg(pl.len().alias("count")) # create a new column containing the count of each genre that appears for each user
        # sort per user by count descending, false for userId since i want it to start from lowest user Id and true
        # for count since i want highest counts
        .sort(["userId", "count"], descending=[False, True])
        .group_by("userId")
        .head(3) # take top 3 per user
        .group_by("userId") # group by userId so i can aggregate based on this
        # aggregate the individual rows into one list containing top 3 genres for each userId
        .agg(pl.col("genres_normalized").alias("top3_genres"))
    )

    print(f"Unique users in genres_df: {genres_df['userId'].n_unique()}")
    print(f"Max userId in genres_df: {genres_df['userId'].max()}")
    print(f"User 609 present in genres_df? {genres_df.filter(pl.col('userId') == 608).height > 0}")

    # Find missing user
    all_users = set(range(609))  
    present_users = set(genres_df['userId'].to_list())
    missing_users = all_users - present_users
    print(f"Missing user IDs: {missing_users}")

    # Save top-3 genres as CSV for hard negative sampling
    genres_df_export = genres_df.with_columns(
        pl.col("top3_genres").list.join("|").alias("genres")
    ).select(["userId", "genres"])
    genres_df_export.write_csv(user_genre_path)
    print(f"Saved user top-3 genres to {user_genre_path}")

    # extracting the col containing the top 3 genres list
    genres = genres_df["top3_genres"].to_list()

    # creating the matrix for each user's preferred genre
    # it creates an array with size of the total genres, then
    # sets it to 1 if the genre shows up for the user and 0 otherwise
    genre_matrix = genre_mlb.transform(genres)

    np.save(genre_output, genre_matrix) # save the numpy file