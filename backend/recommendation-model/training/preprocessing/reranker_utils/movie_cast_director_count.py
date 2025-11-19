import polars as pl

# feature engineering for cast and director count in each movie
def movie_cast_director_count(reranker_feature_path: str, movie_metadata_path: str) -> None:
    reranker_features_df = pl.read_csv(reranker_feature_path)
    metadata_df = pl.read_csv(movie_metadata_path).select(["movie_idx", "cast_normalized", "director"])

    # add the string of cast and director for each movie to the df
    cast_director_df = reranker_features_df.join(
        metadata_df,
        on="movie_idx",
        how="left"
    )

    # convert the pipe seperated string of actors/director to a list so we can count length of list
    # and get the amount of actors/directors for each movie
    num_genres_df = cast_director_df.with_columns(
        pl.col("cast_normalized").str.split("|").list.len().alias("num_cast"),
        pl.col("director").str.split("|").list.len().alias("num_directors")
    )
    
    num_genres_df.write_csv(reranker_feature_path)