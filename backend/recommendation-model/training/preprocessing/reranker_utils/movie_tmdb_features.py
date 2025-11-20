import polars as pl

# extract the tmdb api features for the movie
def movie_tmdb_features(reranker_movie_features_path: str, movie_metadata_path: str) -> None:
    reranker_features_df = pl.read_csv(reranker_movie_features_path)
    metadata_df = (
        pl.read_csv(movie_metadata_path)
        .select(["movie_idx", "vote_average", "vote_count", "popularity", "runtime"])
    )

    # add basic features from movie metadata csv to the reranker csv
    rated_movies_with_metadata_df = reranker_features_df.join(
        metadata_df,
        on="movie_idx",
        how="left"
    ).rename({
        "vote_average": "tmdb_vote_average",
        "vote_count": "tmdb_vote_count",
        "popularity": "tmdb_popularity",
    })

    # creates a 0 or 1 in a new column, 1 (true) if the tmdb_vote_count is greater than 0
    has_tmdb_data_df = rated_movies_with_metadata_df.with_columns(
        (pl.col("tmdb_vote_count") > 0)
        .cast(pl.Int8)
        .alias("has_tmdb_data")
    )

    # create log value of vote count to smooth out the vote count
    # so that larger numbers are weighted less
    vote_count_log = has_tmdb_data_df.with_columns(
        pl.col("tmdb_vote_count")
        .log1p()
        .alias("tmdb_vote_count_log")
        .round(3)
    )

    # normalize runtime within 180 mins as 0, 1, round to 3 digits
    runtime_normalized_df = (
        vote_count_log
        .with_columns(
            (pl.col("runtime") / 180)
            .clip(0, 1)
            .round(3)
            .alias("runtime_normalized")  
        )
    )

    runtime_normalized_df.write_csv(reranker_movie_features_path)