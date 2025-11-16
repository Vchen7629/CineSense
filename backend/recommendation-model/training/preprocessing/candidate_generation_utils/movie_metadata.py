import os
import polars as pl

current_dir = os.path.dirname(__file__)

# creates a new movie-metadata.csv containing movie metadata
def create_movies_metadata(large_dataset: bool = False):
    if large_dataset:
        input_links_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest", "links.csv")
        missing_metadata_output_path = os.path.join(current_dir, "..", "..", "datasets", "output", "missing-metadata.csv")
        pruned_movies_path = os.path.join(current_dir, "..", "..", "datasets", "output", "movie-output.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output", "movie-metadata.csv")
    else:
        input_links_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest-small", "links.csv")
        missing_metadata_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "missing-metadata.csv")
        pruned_movies_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "movie-output.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "..","datasets", "output-small", "movie-metadata.csv")
    
    input_movies_metadata = os.path.join(current_dir, "..", "..", "datasets", "metadata", "TMDB_all_movies_cleaned.csv")
    movie_df = pl.read_csv(pruned_movies_path)
    links_df = pl.read_csv(input_links_path, dtypes={"imdbId": pl.Utf8})
    metadata_df = pl.read_csv(input_movies_metadata)

    # create a dataframe with imdbid so we can filter with imdbId later
    movie_df = movie_df.join(links_df, on="movieId", how="left")

    metadata_df = metadata_df.with_columns([
        pl.col("imdb_id") 
            .str.replace_all(r"tt", "")
            .alias("imdb_new_id"),
        pl.col("genres")
            .str.replace_all(r"Sci-Fi & Fantasy", "Science Fiction|Fantasy")
            .str.replace_all(r"Action & Adventure", "Action|Adventure")
            .str.replace_all(r"War & Politics", "War|Politics")
            .str.replace_all(r", ", "|")
            .alias("genres_normalized"),
        pl.col("cast")
            .str.replace_all(r", ", "|")
            .alias("cast_normalized"),
        pl.col("director")
            .str.replace_all(r", ", "|")
            .alias("director")
    ]).drop([
        "id",
        "vote_average", 
        "vote_count", 
        "status", 
        "revenue",
        "runtime",
        "budget",
        "genres",
        "imdb_id",
        "cast",
        "original_language",
        "original_title",
        "popularity",
        "tagline",
        "production_companies",
        "production_countries",
        "spoken_languages",
        "director_of_photography",
        "writers",
        "producers",
        "music_composer",
        "imdb_rating",
        "imdb_votes",
        "release_date",
        "genres"
    ])


    joined_on_imdb = movie_df.join(
        metadata_df,
        left_on="imdbId",
        right_on="imdb_new_id",
        how="left"
    ).drop(["genres", "title_right"])

    # find the rows that dont have director or cast values (null or empty string)
    missing_metadata = joined_on_imdb.filter(
        (pl.col("director").is_null()) | (pl.col("director").str.len_chars() == 0) |
        (pl.col("cast_normalized").is_null()) | (pl.col("cast_normalized").str.len_chars() == 0) |
        (pl.col("genres_normalized").is_null()) | (pl.col("genres_normalized").str.len_chars() == 0)
    ).select(["movieId", "title", "imdbId", "year"])


    joined_on_imdb.write_csv(movie_metadata_path)

    missing_metadata.write_csv(missing_metadata_output_path)
