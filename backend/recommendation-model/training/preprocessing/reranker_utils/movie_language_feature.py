import polars as pl

def movie_language_feature(reranker_features_path: str, movie_metadata_path: str):
    language_df = pl.read_csv(movie_metadata_path).select(["tmdbId", "original_language"])
    reranker_features_df = pl.read_csv(reranker_features_path)

    reranker_features_df = reranker_features_df.join(
        language_df,
        how="left",
        on="tmdbId"
    )

    print(reranker_features_df)
