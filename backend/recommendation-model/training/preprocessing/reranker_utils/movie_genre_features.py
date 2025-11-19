import polars as pl

# feature engineering for movie genre related features
def movie_genre_features(reranker_feature_path: str, movie_metadata_path: str) -> None:
    reranker_features_df = pl.read_csv(reranker_feature_path)
    metadata_df = pl.read_csv(movie_metadata_path).select(["movie_idx", "genres_normalized"])

    # add the list of genres to the df
    genres_df = reranker_features_df.join(
        metadata_df,
        on="movie_idx",
        how="left"
    )

    num_genres_df = genres_df.with_columns(
        pl.col("genres_normalized").str.split("|").list.len().alias("num_genres")
    )

    num_genres_df.write_csv(reranker_feature_path)