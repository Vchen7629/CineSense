import polars as pl
import os

# helper function to create movie year related features such as release year, movie age in years, and recency score
def movie_year_features(reranker_features_path: str, movie_metadata_path: str) -> None:
    movie_ids_df = pl.read_csv(reranker_features_path).select(["tmdbId"])
    reranker_features_df = pl.read_csv(reranker_features_path)
    movie_metadata_df = pl.read_csv(movie_metadata_path).select(["tmdbId","year"])

    year_df = movie_ids_df.join(
        movie_metadata_df,
        on="tmdbId",
        how="left"
    )

    # add movie year to the df
    reranker_features_df = year_df.join(
        reranker_features_df,
        how="left",
        on="tmdbId"
    )

    # calculate movie age by subtracting current year (2025) by movie age
    age_df = (
        year_df
            .with_columns((2025 - pl.col("year")).alias("movie_age"))
            .drop("year")
    )

    # add movie age to the df
    reranker_features_df = age_df.join(
        reranker_features_df,
        how="left",
        on="tmdbId"
    )

    # calculate recency with formula: 1 - min((2025 - year) / 50, 1.0) to normalize it between 0 and 1
    recency_score_df = (
        year_df
            .with_columns(
                (
                    ((1 - ((2025 - pl.col("year")) / 50).clip(0, 1)) * 1000)
                    .ceil()
                    / 1000
                ).alias("recency_score")
            )
            .drop("year")
    )

    # add the recency score to the df
    reranker_features_df = recency_score_df.join(
        reranker_features_df,
        how="left",
        on="tmdbId"
    )

    reranker_features_df.write_csv(reranker_features_path)