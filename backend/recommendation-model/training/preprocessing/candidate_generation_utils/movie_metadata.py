import polars as pl
from shared.path_config import path_helper

# creates a new movie-metadata.csv containing movie metadata
def create_movies_metadata(large_dataset: bool = False):
    paths = path_helper(large_dataset=large_dataset)

    input_links_path = paths.movielens_links_path
    missing_metadata_output_path = paths.missing_movie_metadata_path
    pruned_movies_path = paths.pruned_movies_path
    movie_metadata_path = paths.movie_metadata_path
    input_movies_metadata = paths.tmdb_all_movies_cleaned_path

    movie_df = pl.read_csv(pruned_movies_path)
    links_df = pl.read_csv(input_links_path, dtypes={"imdbId": pl.Utf8})
    metadata_df = pl.read_csv(input_movies_metadata)

    # create a dataframe with imdbid so we can filter with imdbId later
    movie_df = movie_df.join(links_df, on="movieId", how="left")

    # Normalize IMDB IDs: MovieLens has "114709", but APIs need "tt0114709"
    # Add "tt" prefix and pad with leading zeros to 7 digits
    movie_df = movie_df.with_columns([
        ("tt" + pl.col("imdbId").str.zfill(7)).alias("imdbId")
    ])

    print("hi",movie_df.columns)

    metadata_df = metadata_df.with_columns([
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
            .alias("director"),
        # Extract year from release_date (YYYY-MM-DD format)
        pl.col("release_date").str.slice(0, 4).cast(pl.Int64, strict=False).alias("year")
    ]).drop([
        "id",
        "status",
        "revenue",
        "budget",
        "genres",
        "cast",
        "original_title",
        "tagline",
        "production_companies",
        "production_countries",
        "spoken_languages",
        "director_of_photography",
        "writers",
        "producers",
        "music_composer",
        "release_date",
        "genres"
    ])

    print(metadata_df.columns)

    # Join on IMDB ID (unique and correct) instead of TMDB ID (has duplicates)
    # This ensures we get the correct movie metadata
    joined_on_imdb = movie_df.join(
        metadata_df,
        left_on="imdbId",
        right_on="imdb_id",
        how="left"
    )

    # Drop duplicate/unnecessary columns after join
    cols_to_drop = []
    if "title_right" in joined_on_imdb.columns:
        cols_to_drop.append("title_right")
    if "imdb_id" in joined_on_imdb.columns:
        cols_to_drop.append("imdb_id")
    if "genres" in joined_on_imdb.columns:
        cols_to_drop.append("genres")

    if cols_to_drop:
        joined_on_imdb = joined_on_imdb.drop(cols_to_drop)

    # find the rows that dont have director or cast values (null or empty string)
    missing_metadata = joined_on_imdb.filter(
        (pl.col("director").is_null()) | (pl.col("director").str.len_chars() == 0) |
        (pl.col("cast_normalized").is_null()) | (pl.col("cast_normalized").str.len_chars() == 0) |
        (pl.col("genres_normalized").is_null()) | (pl.col("genres_normalized").str.len_chars() == 0) |
        (pl.col("year").is_null()) | (pl.col("year").cast(pl.String).str.len_chars() == 0) |
        (pl.col("overview").is_null()) | (pl.col("overview").str.len_chars() == 0)
    ).select(["movieId", "title", "imdbId", "year"])


    joined_on_imdb.write_csv(movie_metadata_path)

    missing_metadata.write_csv(missing_metadata_output_path)
