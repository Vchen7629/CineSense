import polars as pl

# calculate the average rating of a feature
def avg_rating(
    feature_id: str,
    column_name: str,
    new_col_name: str,
    reranker_features_path: str,
    pos_ratings_path: str, 
    neg_ratings_path: str
) -> None:
    pos_ratings_df = pl.read_csv(pos_ratings_path)
    neg_ratings_df = pl.read_csv(neg_ratings_path)
    all_ratings_df = pl.concat([pos_ratings_df, neg_ratings_df], how="vertical")
    reranker_df = pl.read_csv(reranker_features_path)

    # get ratings total (sum of all ratings) for the feature
    feature_ratings_count = (
        all_ratings_df
            .group_by(feature_id)
            .agg(
                pl.sum("rating").alias("total_rating")
            )
            .sort(feature_id)
    )

    # join on id
    reranker_df = reranker_df.join(
        feature_ratings_count,
        how="left",
        on=feature_id
    )

    # find average rating for each feature item
    avg_rating_df = (
        reranker_df
            .with_columns(
                (pl.col("total_rating") / pl.col(column_name))
                .alias(new_col_name)
            )
            .drop("total_rating")
            
    )

    avg_rating_df.write_csv(reranker_features_path)