import polars as pl
import os

# preprocessing script that generates top 50 favorite actors and top 10 favorite directors
# for each user in the dataset based on their rated movies and writes to csv to be used later
def generate_favorite_cast_director(
    movie_metadata_path: str, 
    user_pos_rating_path: str, 
    large_dataset: bool = False
) -> None: 
    current_dir = os.path.dirname(__file__)

    if large_dataset:
        favorite_actor_dir_path = os.path.join(current_dir, "..", "..", "datasets", "output", "favorite-actor-directors.csv")
    else:
        favorite_actor_dir_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "favorite-actor-directors.csv")

    metadata_df = pl.read_csv(movie_metadata_path).select(["tmdbId", "cast_normalized", "director"])
    pos_rating_df = pl.read_csv(user_pos_rating_path).select(["userId", "tmdbId"])
    favorite_actor_director_df = pl.read_csv(user_pos_rating_path).select("userId")

    actors_director_df = pos_rating_df.join(
        metadata_df,
        how="left",
        on="tmdbId"
    )  

    print(actors_director_df)

    # get top 50 actors per user
    top_actors_df = (
        actors_director_df
        .with_columns(
            pl.col("cast_normalized").str.split("|").alias("cast_list")
        )
        .explode("cast_list") # one row per actor
        .group_by(["userId", "cast_list"])
        .agg(pl.len().alias("actor_count"))
        .sort(["userId", "actor_count"], descending=[False, True])
        .group_by("userId")
        .agg( # get top 50 actors, convert it to string from list
            pl.col("cast_list").head(50).str.join(delimiter="|").alias("top_50_actors")
        )
    )

    # get top 10 directors per user
    top_directors_df = (
        actors_director_df
        .with_columns(
            pl.col("director").str.split("|").alias("director_list")
        )
        .explode("director_list") # one row per director
        .group_by(["userId", "director_list"])
        .agg(pl.len().alias("director_count"))
        .sort(["userId", "director_count"], descending=[False, True])
        .group_by("userId")
        .agg( # get top 10 director, convert it to string from list
            pl.col("director_list").head(10).str.join(delimiter="|").alias("top_10_directors")
        )
    )

    output_df = favorite_actor_director_df.unique("userId").sort("userId")

    top_actors_df = top_actors_df.join(
        output_df,
        how="left",
        on="userId"
    )

    top_actors_director_df = top_actors_df.join(
        top_directors_df,
        how="left",
        on="userId"
    )

    top_actors_director_df.write_csv(favorite_actor_dir_path)

    