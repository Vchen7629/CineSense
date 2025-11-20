import polars as pl

# feature engineering for calculating the num of genres/actors/directors the
# user likes based on their positively rated history
def user_num_liked_feature(
    feature_col_name: str,
    new_col_name: str,
    reranker_feature_path: str, 
    movie_metadata_path: str, 
    pos_ratings_path: str
) -> None:
    reranker_features_df = pl.read_csv(reranker_feature_path)
    metadata_df = pl.read_csv(movie_metadata_path).select(["movie_idx", feature_col_name])
    pos_ratings_df = pl.read_csv(pos_ratings_path)

    pos_movies_metadata_df = pos_ratings_df.join(
        metadata_df,
        on="movie_idx",
        how="left"
    )

    # count the number of genres in user's positively rated movies    
    genre_count_df = (
        pos_movies_metadata_df
        .with_columns(
            pl.col(feature_col_name).str.split("|").alias("feature_list")
        )
        .group_by("userId")
        .agg(
            pl.col("feature_list").flatten().len().alias(new_col_name)
        )
        .sort("userId")
    )

    genre_count_df = reranker_features_df.join(
        genre_count_df,
        on="userId",
        how="left"
    )

    genre_count_df.write_csv(reranker_feature_path)
