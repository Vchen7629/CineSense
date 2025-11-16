import polars as pl
import os
from typing import Optional
import re

current_dir = os.path.dirname(__file__)

# removes invisible unicode marks like U+200E and makes multi line quotes into one line
def clean_csv():
    input_movies_metadata = os.path.join(current_dir, "..", "datasets", "metadata", "TMDB_all_movies.csv")
    output_clean = os.path.join(current_dir, "..", "datasets", "metadata", "TMDB_all_movies_cleaned.csv")
    hidden_chars = re.compile(r'[\u2028\u2029\u200E\u200F\u202A-\u202E\uFEFF]')

    with open(input_movies_metadata, "r", encoding="utf-8", errors="replace") as infile, \
        open(output_clean, "w", encoding="utf-8", newline="") as outfile:
        
        buffer = ""
        for line in infile:
            # Remove invisible unicode marks
            line = hidden_chars.sub("", line)
            buffer += line.rstrip("\r\n")
            
            # Count quotes so we know if we're inside or outside
            if buffer.count('"') % 2 == 0:
                # Finished a row — write and reset
                outfile.write(buffer + "\n")
                buffer = ""
            else:
                # Still inside a quoted field — keep merging
                buffer += " "
        
        if buffer.strip():  # write any remaining
            outfile.write(buffer + "\n")

    print(f"✅ Cleaned and fixed CSV written to: {os.path.abspath(output_clean)}")

# Validate and update outdated IMDB IDs in links.csv by matching with TMDB data
def update_imdb_ids():
    input_movie_path = os.path.join(current_dir, "..", "datasets", "output", "movie-output.csv")
    input_movies_metadata = os.path.join(current_dir, "..", "datasets", "metadata", "TMDB_all_movies_cleaned.csv")
    input_links_path = os.path.join(current_dir, "..", "datasets", "latest-latest", "links.csv")
    
    movie_df = pl.read_csv(input_movie_path)
    links_df = pl.read_csv(input_links_path, dtypes={"imdbId": pl.Utf8})
    metadata_df = pl.read_csv(input_movies_metadata)

    # extract title into title and year from movie_df: "Presto (2008)" -> "Presto" + "2008"
    movie_df = movie_df.with_columns([
        pl.col("title").str.replace(r'\s*\(\d{4}\)$', '').alias("title_no_year"),
        pl.col("title").str.extract(r'\((\d{4})\)$', 1).alias("year"),
        pl.col("genres").str.split("|").alias("genre_list")
    ]).with_columns([
        # normalize title by removing punctuation, lowercase
        pl.col("title_no_year")
            .str.to_lowercase()
            .str.replace_all(r"[,\.:\-'\"!?]", "")
            .alias("title_normalized")
    ]).drop(["title", "genres", "movie_idx"])

    updated_tmdb_df = metadata_df.with_columns([
        # extract year from release_date in metadata df "1999-10-21" -> "1999"
        pl.col("release_date").str.slice(0, 4).alias("year"),
        pl.col("title")
            .str.to_lowercase()
            .str.replace_all(r"[,\.:\-'\"!?]", "")
            .alias("title_normalized"),
        pl.col("original_title")
            .str.to_lowercase()
            .str.replace_all(r"[,\.:\-'\"!?]", "")
            .alias("original_title_normalized"),
        pl.col("imdb_id") 
            .str.replace_all(r"tt", "")
            .alias("updated_imdb_id"),
        pl.col("genres")
            .str.replace_all(r", ", "|")
            .str.split("|")
            .alias("genre_list")
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
        "original_language",
        "original_title",
        "overview",
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
        "poster_path",
        "release_date",
        "genres",
        "director",
        "cast"
    ])

    # join movies with the links to get current imdb ids
    movies_with_links = movie_df.join(links_df, on="movieId", how="left")

    # join with tmdb on title + year to get correct imdb id
    joined_on_title = movies_with_links.join(
        updated_tmdb_df.select(["title_normalized", "year", "updated_imdb_id", "genre_list"]),
        on=["title_normalized", "year"],
        how="left",
    ).rename({"updated_imdb_id": "updated_imdb_id_title"})

    # try matching with original title if not matched
    joined_on_title = joined_on_title.join(
        updated_tmdb_df.select(["original_title_normalized", "year", "updated_imdb_id"]),
        left_on=["title_normalized", "year"],
        right_on=["original_title_normalized", "year"],
        how="left",
    ).rename({"updated_imdb_id": "updated_imdb_id_orig"})

    matched_with_genre_check = joined_on_title.with_columns([
        pl.col("genre_list").list.set_intersection(pl.col("genre_list_right")).list.len().alias("genre_overlap_count")
    ]).filter(
        pl.col("genre_overlap_count") > 0
    )

    # keep the one with most genre overlap
    best_matches = matched_with_genre_check.sort("genre_overlap_count", descending=True).unique(subset=["movieId"], keep="first")

    # coalesce to combine both columns into one with the non null value
    final_match = best_matches.with_columns([
        pl.coalesce([pl.col("updated_imdb_id_title"), pl.col("updated_imdb_id_orig")]).alias("updated_imdb_id")
    ]).drop(["updated_imdb_id_title", "updated_imdb_id_orig"])

    # find mismatches - imdbId is different from updated_imdb_id
    mismatches = final_match.filter(
        (pl.col("imdbId") != pl.col("updated_imdb_id")) &
        (pl.col("updated_imdb_id").str.len_chars() > 0)
    ).select(["movieId", "imdbId", "updated_imdb_id"]).unique(subset=["movieId"], keep="first")

    print(f"Found {mismatches.height} movies with outdated imdb ids")
    print(mismatches)

    if mismatches.height > 0:
        # update links.csv
        updated_links = links_df.join(
            mismatches.select(["movieId", "updated_imdb_id"]),
            on="movieId",
            how="left",
        )

        # update the imdbId value with updated_imdb_id col value if its non null
        # otherwise keep using the old imdbId
        updated_links = updated_links.with_columns([ 
            pl.coalesce([pl.col("updated_imdb_id"), pl.col("imdbId")]).alias("imdbId")
        ]).drop("updated_imdb_id")

        #updated_links.write_csv(input_links_path)

    # create a new df that has the imdb tmdb id links
    #missing_df = missing_metadata.join(links_df, on="movieId", how="inner")

    #print(missing_df)

    #metadata_df.write_csv(movies_output_path)

    #missing_metadata.write_csv(missing_metadata_output_path)

if __name__ == "__main__":
    clean_csv()
    #update_imdb_ids()