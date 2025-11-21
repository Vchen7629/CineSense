import os
import polars as pl

# remove invalid movies
def remove_invalid_movies(
        movies_path: str,
        links_path: str,
        mismatched_id_path: str,
        large_dataset: bool = False
    ):
    current_dir = os.path.dirname(__file__)

    if large_dataset:
        ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest", "ratings.csv")
    else:
        ratings_path = os.path.join(current_dir, "..", "..", "datasets", "ml-latest-small", "ratings.csv")

    mismatched_id_df = pl.read_csv(mismatched_id_path)
    links_df = pl.read_csv(links_path)
    movies_df = pl.read_csv(movies_path)
    ratings_df = pl.read_csv(ratings_path)

    # Check if the mismatched_id_df is empty
    if len(mismatched_id_df) == 0:
        print("No invalid movies to remove - mismatched IDs file is empty")
        return

    # Check if 'issue' column exists (for imdb_mismatches.csv)
    # Auto-remove TV shows and 404 not found
    if "issue" in mismatched_id_df.columns:
        # Filter for TV shows and 404s to remove
        invalid_movies_df = mismatched_id_df.filter(
            (pl.col("issue") == "TV Show") | (pl.col("issue") == "404 Not Found")
        )

        if len(invalid_movies_df) == 0:
            print("No TV shows or 404s to remove")
            return

        # Show breakdown
        tv_shows_count = invalid_movies_df.filter(pl.col("issue") == "TV Show").height
        not_found_count = invalid_movies_df.filter(pl.col("issue") == "404 Not Found").height

        print(f"Removing {len(invalid_movies_df)} movies:")
        print(f"  TV shows: {tv_shows_count}")
        print(f"  404 Not Found: {not_found_count}")

        # Show other issues that are NOT being removed
        other_issues = mismatched_id_df.filter(
            (pl.col("issue") != "TV Show") & (pl.col("issue") != "404 Not Found")
        )
        if len(other_issues) > 0:
            print(f"\nKeeping {len(other_issues)} movies with other issues for manual review:")
            issue_counts = other_issues.group_by("issue").agg(pl.count()).sort("count", descending=True)
            for row in issue_counts.iter_rows(named=True):
                print(f"  {row['issue']}: {row['count']}")
    else:
        # No issue column - this shouldn't happen with new pipeline
        print("Warning: No 'issue' column found in mismatches file")
        return

    # If nothing to remove, don't modify the files
    if len(invalid_movies_df) == 0:
        print("No movies to remove - skipping file updates")
        return

    # filter out movies in links csv matching the movieId
    filtered_links_df = links_df.join(
        invalid_movies_df.select("movieId"),
        on="movieId",
        how="anti"
    )

    # filter out movies in movies csv matching the movieId
    filtered_movies_df = movies_df.join(
        invalid_movies_df.select("movieId"),
        on="movieId",
        how="anti"
    )

    # filter out movies in ratings csv matching the movieId
    filtered_ratings_df = ratings_df.join(
        invalid_movies_df.select("movieId"),
        on="movieId",
        how="anti"
    )

    # update the csvs
    filtered_links_df.write_csv(links_path)
    filtered_movies_df.write_csv(movies_path)
    filtered_ratings_df.write_csv(ratings_path)

