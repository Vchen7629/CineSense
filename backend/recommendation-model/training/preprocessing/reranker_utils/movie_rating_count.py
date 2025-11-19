import polars as pl

# calculate the amount of user ratings corresponding to each movie
def movie_rating_count(reranker_features_path: str, pos_ratings_path: str, neg_ratings_path: str) -> None:
    pos_ratings_df = pl.read_csv(pos_ratings_path)
    neg_ratings_df = pl.read_csv(neg_ratings_path)
    all_ratings_df = pl.concat([pos_ratings_df, neg_ratings_df], how="vertical")

    tmdb_id_df = all_ratings_df.select(["movie_idx", "tmdbId"]).unique().sort("movie_idx")

    rating_count_df = (
        all_ratings_df
            .group_by("movie_idx")
            .len()
            .sort("movie_idx")
            .rename({"len": "movie_rating_count"})
            .select(["movie_idx", "movie_rating_count"])
    )

    # add tmdbId to each row
    rating_count_df = rating_count_df.join(
        tmdb_id_df,
        how="left",
        on="movie_idx"
    )

    # create log value of rating count to smooth out the rating count
    # so that larger ratings are weighted less
    rating_count_log_df = rating_count_df.with_columns(
        pl.col("movie_rating_count")
        .log1p()
        .round(3)
        .alias("movie_rating_log")
    )


    rating_count_log_df.write_csv(reranker_features_path)