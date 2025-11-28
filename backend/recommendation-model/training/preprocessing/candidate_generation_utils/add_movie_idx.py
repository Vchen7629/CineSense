import polars as pl
from ..shared.extract_year import extract_title_without_year, extract_year_from_title
from shared.path_config import path_helper

# prunes movie.csv to only unique movies and creates a idx mapping for user to movie dataset
def add_movie_user_idx_mapping(
    positive_ratings_path: str,
    negative_ratings_path: str,
    large_dataset: bool = False
):
    paths = path_helper(large_dataset=large_dataset)
    input_movie_path = paths.movielens_movies_path
    pruned_movies_path = paths.pruned_movies_path

    pos_ratings_df = pl.read_csv(positive_ratings_path)
    neg_ratings_df = pl.read_csv(negative_ratings_path)
    movies_df = pl.read_csv(input_movie_path)

    # get all unique movie ids in the user dataset and prune movie dataset to only include those
    unique_movies_pos = pos_ratings_df.select("movieId").unique()
    unique_movies_neg = neg_ratings_df.select("movieId").unique()
    unique_movies = pl.concat([unique_movies_pos, unique_movies_neg]).unique().to_series()

    pruned_movie_df = movies_df.filter(pl.col("movieId").is_in(unique_movies))

    # add continuous movie_idx starting from 0
    pruned_movie_df = pruned_movie_df.with_row_index(name="movie_idx")

    # Extract year from title and clean title
    pruned_movie_df = pruned_movie_df.with_columns([
        pl.col("title").map_elements(extract_year_from_title, return_dtype=pl.Int64).alias("year"),
        pl.col("title").map_elements(extract_title_without_year, return_dtype=pl.Utf8).alias("title")
    ])

    print(f"Pruned movie columns: {pruned_movie_df.columns}")
    print(f"Sample rows:\n{pruned_movie_df.head()}")
    print(f"total unique movies: {len(pruned_movie_df)}")

    # join ratings files with pruned_movie_df to add movie_idx column to each file
    pos_ratings_df = pos_ratings_df.join(
        pruned_movie_df.select(['movieId', 'movie_idx']),
        on="movieId",
        how="left"
    )

    neg_ratings_df = neg_ratings_df.join(
        pruned_movie_df.select(['movieId', 'movie_idx']),
        on="movieId",
        how="left"
    )

    # Filter out rows where movie_idx is null (movies that don't exist in pruned_movie_df)
    pos_ratings_df = pos_ratings_df.filter(pl.col('movie_idx').is_not_null())
    neg_ratings_df = neg_ratings_df.filter(pl.col('movie_idx').is_not_null())

    # create new csv containing only the movies that the users rated
    pruned_movie_df.write_csv(pruned_movies_path)

    # update both user ratings files to contain the movie_idx mappings
    pos_ratings_df.write_csv(positive_ratings_path)
    neg_ratings_df.write_csv(negative_ratings_path)
