import polars as pl

def movie_language_feature(reranker_features_path: str, movie_metadata_path: str):
    language_df = pl.read_csv(movie_metadata_path).select(["movie_idx", "original_language"])
    reranker_features_df = pl.read_csv(reranker_features_path)

    reranker_features_df = reranker_features_df.join(
        language_df,
        how="left",
        on="movie_idx"
    )

    hi = reranker_features_df['original_language'].value_counts().sort("count", descending=True)
    print(hi.head(50))

    reranker_features_df.write_csv(reranker_features_path)

