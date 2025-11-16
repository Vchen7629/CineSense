import os
import polars as pl

current_dir = os.path.dirname(__file__)

# prunes movie.csv to only unique movies and creates a idx mapping for user to movie dataset
def add_movie_user_idx_mapping(large_dataset: bool = False):
    if large_dataset:
        input_user_path = os.path.join(current_dir, "..", "..", "datasets", "output", "user-output.csv")
        input_movie_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest", "movies.csv")
        pruned_movies_path = os.path.join(current_dir, "..", "..", "datasets", "output", "movie-output.csv")
    else:
        input_user_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "user-output.csv")
        input_movie_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest-small", "movies.csv")
        pruned_movies_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "movie-output.csv")

    user_df = pl.read_csv(input_user_path)
    movies_df = pl.read_csv(input_movie_path)

    # get all unique movie ids in the user dataset and prune movie dataset to only include those
    unique_title = user_df['movieId'].unique()
    pruned_movie_df = movies_df.filter(pl.col("movieId").is_in(unique_title))

    # add continuous movie_idx starting from 0
    pruned_movie_df = pruned_movie_df.with_row_index(name="movie_idx")

    print(f"Pruned movie columns: {pruned_movie_df.columns}")
    print(f"Sample rows:\n{pruned_movie_df.head()}")

    # join user_df with pruned_movie_df to add movie_idx column
    user_df = user_df.join(
        pruned_movie_df.select(['movieId', 'movie_idx']),
        on="movieId",
        how="left"
    )

    print(f"User df columns: {user_df.columns}")

    # create new csv containing only the movies that the users rated
    pruned_movie_df.write_csv(pruned_movies_path)

    # update the user csv to contain the mappings
    user_df.write_csv(input_user_path)