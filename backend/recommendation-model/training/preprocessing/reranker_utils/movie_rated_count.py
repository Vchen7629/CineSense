import polars as pl

# calculate the amount of user ratings corresponding to each movie
def movie_rating_count(reranker_features_path: str, pos_ratings_path: str, neg_ratings_path: str) -> None:
    pos_ratings_df = pl.read_csv(pos_ratings_path)
    neg_ratings_df = pl.read_csv(neg_ratings_path)
    all_ratings_df = pl.concat([pos_ratings_df, neg_ratings_df], how="vertical")

    movie_count_df = (
        all_ratings_df
            .group_by("tmdbId")
            .len()
            .sort("tmdbId")
            .rename({"len": "movie_rating_count"})
    )
    print(movie_count_df)

    movie_count_df = movie_count_df.select(["tmdbId", "movie_rating_count"])

    movie_count_df.write_csv(reranker_features_path)