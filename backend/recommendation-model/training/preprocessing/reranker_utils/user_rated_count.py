import polars as pl

# preprocessing 
def user_rated_movie_count(reranker_user_features_path: str, pos_ratings_path: str, neg_ratings_path: str) -> None:
    pos_ratings_df = pl.read_csv(pos_ratings_path)
    neg_ratings_df = pl.read_csv(neg_ratings_path)
    all_ratings_df = pl.concat([pos_ratings_df, neg_ratings_df], how="vertical")

    ratings_df = (
        all_ratings_df
            .group_by("userId")
            .len()
            .sort("userId")
            .rename({"len": "user_rating_count"})
    )
    print(ratings_df)

    # create log value of rating count to smooth out the rating count
    # so that larger ratings are weighted less
    rating_count_log_df = ratings_df.with_columns(
        pl.col("user_rating_count")
        .log1p()
        .round(3)
        .alias("user_rating_log")
    )

    reranker_df = rating_count_log_df.select(["userId", "user_rating_count", "user_rating_log"])

    reranker_df.write_csv(reranker_user_features_path)