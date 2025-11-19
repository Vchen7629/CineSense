import os
import polars as pl

# remove invalid movies
def remove_invalid_movies(
        movies_path: str, 
        links_path: str, 
        mismatched_id_path: str, 
        large_dataset: bool = False,
        filter_tvshows: bool = True
    ):
    current_dir = os.path.dirname(__file__)

    if large_dataset:
        ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest", "ratings.csv")
    else:
        ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest-small", "ratings.csv")

    mismatched_id_df = pl.read_csv(mismatched_id_path)
    links_df = pl.read_csv(links_path)
    movies_df = pl.read_csv(movies_path)
    ratings_df = pl.read_csv(ratings_path)

    if filter_tvshows:
        invalid_movies_df = mismatched_id_df.select("movieId")
    else:
        # filter for the columns containing this value
        invalid_movies_df = mismatched_id_df.filter(
            pl.col("issue") == "TMDB ID not found (404)"
        ).select("movieId")

    # filter out movies in links csv matching the movieId
    filtered_links_df = links_df.join(
        invalid_movies_df.select("movieId"),
        on="movieId",
        how="anti"
    )


    # filter out movies in movies csv matching the movieId
    filtered_movies_df = movies_df.join(
        invalid_movies_df.select("movieId"),
        on="movieId",
        how="anti"
    )

    # filter out movies in ratings csv matching the movieId
    filtered_ratings_df = ratings_df.join(
        invalid_movies_df.select("movieId"),
        on="movieId",
        how="anti"
    )

    # update the csvs
    filtered_links_df.write_csv(links_path)
    filtered_movies_df.write_csv(movies_path)
    filtered_ratings_df.write_csv(ratings_path)

