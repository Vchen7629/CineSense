import asyncio
import aiohttp
import polars as pl
from typing import List
from utils.env_config import settings

# Load environment variables
TMDB_API_KEY = settings.TMDB_API_KEY
TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def get_genres(session: aiohttp.ClientSession, tmdb_id: int, semaphore: asyncio.Semaphore):
    """ Get a list of genres to check with duplicate movies """
    async with semaphore:
        headers = {'Authorization': f'Bearer {TMDB_API_KEY}'}
        movie_url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?language=en-US"

        try:
            async with session.get(movie_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # extract genre names from api res
                    genres = data.get('genres', [])
                    genre_names = [genre['name'] for genre in genres]

                    return {
                        'tmdbId': tmdb_id,
                        'genres': genre_names
                    }

        except Exception as e:
            print(f"Exception checking TMDB ID {tmdb_id}: {e}")
            return []
        
async def check_all_ids(ids_to_check: list, max_concurrent: int = 40):
    """Check all duplicate TMDB IDs to determine their media type."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async with aiohttp.ClientSession() as session:
        tasks = [
            get_genres(session, tmdb_id, semaphore)
            for tmdb_id in ids_to_check
        ]

        results = await asyncio.gather(*tasks)
        
        # Filter out None results (failed requests)
        valid_results = [r for r in results if r is not None]
        
        print(f"Completed checking - found {len(valid_results)} valid entries")

    return pl.DataFrame(valid_results)

def compare_genres(tmdb_genre_df: pl.DataFrame, movies_df: str) -> tuple[pl.DataFrame, List[int], List[int]]:
    movies_to_check_df = tmdb_genre_df.join(
        movies_df,
        on="movieId",
        how="left"
    ).drop("genres")


    comparison_df = movies_to_check_df.with_columns(
        pl.col("dataset_genres").str.split("|").alias("dataset_genres_list")
    ).drop("dataset_genres")

    print("1", comparison_df)

    # calculate overlap between the api genres and dataset genrs
    comparison_df = comparison_df.with_columns([
        # count how many genres overlap
        pl.when(pl.col("dataset_genres_list").is_not_null())
        .then(
            pl.col("dataset_genres_list")
            .list.set_intersection(pl.col("tmdb_genres"))
            .list.len()
        )
        .otherwise(0)
        .alias("overlap_count")
    ])

    print("2", comparison_df)

    # select the movieId with highest overlap for each tmdb
    best_matches_df = (
        comparison_df
        .sort(["tmdbId", "overlap_count"], descending=[False, True])
        .group_by("tmdbId")
        .first()
        .select([
            "tmdbId", 
            "movieId", 
            "overlap_count",
            "tmdb_genres",
            "dataset_genres_list"
        ])
    )

    # identify movies to keep, the ones not selected by best_matches_df
    movies_to_keep = best_matches_df.select("movieId").to_series().to_list()
    movies_to_remove = (
        comparison_df
        .filter(~pl.col("movieId").is_in(movies_to_keep))
        .select(["tmdbId", "movieId", "overlap_count"])
    )

    # create aligned list for mapping
    old_movies_ids = movies_to_remove.select("movieId").to_series().to_list()

    # For each movie to remove, find its corresponding "keep" movieId (same tmdbId)
    new_movie_ids = []
    for row in movies_to_remove.iter_rows(named=True):
        tmdb_id = row['tmdbId']
        new_id = best_matches_df.filter(pl.col("tmdbId") == tmdb_id).select("movieId").item()
        new_movie_ids.append(new_id)
    
    print("3", best_matches_df)
    print("4", movies_to_keep)
    print("5", movies_to_remove)

    return movies_to_remove, old_movies_ids, new_movie_ids

# remove the duplicate movies with less genre overlap
def remove_movies(
    movies_to_remove: pl.DataFrame,
    old_movies_ids: List[int],
    new_movie_ids: List[int], 
    links_path: str,
    movies_path: str,
    ratings_path: str,
    links_df: pl.DataFrame, 
    movies_df: pl.DataFrame, 
    ratings_df: pl.DataFrame
) -> None:
    movies_to_remove_df = movies_to_remove.select("movieId")

    print("idk", movies_to_remove_df)

    # remove duplicate movies in links.csv and movies.csv
    links_df = links_df.join(
        movies_to_remove_df,
        on="movieId",
        how="anti"
    )

    movies_df = movies_df.join(
        movies_to_remove_df,
        on="movieId",
        how="anti"
    )

    # replace movieIds using aligned lists
    for old_id, new_id in zip(old_movies_ids, new_movie_ids):
        ratings_df = ratings_df.with_columns(
            pl.when(pl.col("movieId") == old_id)
            .then(pl.lit(new_id))
            .otherwise(pl.col("movieId"))
            .alias("movieId")
        )

    links_df.write_csv(links_path)
    movies_df.write_csv(movies_path)
    ratings_df.write_csv(ratings_path)

# find duplicate TMDB ids in links.csv and save to the duplicate csv
def remove_duplicate_tmdb_ids(links_path: str, movies_path: str, ratings_path: str, duplicate_ids_path: str):
    # Load data
    links_df = pl.read_csv(links_path)
    movies_df = pl.read_csv(movies_path)
    ratings_df = pl.read_csv(ratings_path)

    # Find duplicate TMDB IDs (excluding null - they're handled by fill_missing_tmdb_ids)
    tmdb_duplicates_df = (
        links_df
            .filter(pl.col("tmdbId").is_not_null())
            .group_by("tmdbId")
            .agg([
                pl.count("movieId").alias("count"),
                pl.col("movieId").alias("movieId")
            ])
            .filter(pl.col("count") > 1)
            .sort("count", descending=True)
            .explode("movieId")
    )

    if len(tmdb_duplicates_df) == 0:
        print("\nNo duplicate TMDB IDs found!")
        return

    print(f"\nFound {len(tmdb_duplicates_df)} duplicate TMDB IDs")
    print(f"Total movies affected: {tmdb_duplicates_df['count'].sum()}")
    print("\nTop duplicates:")
    print(tmdb_duplicates_df.head(10))

    # Save duplicate entries
    tmdb_duplicates_df.write_csv(duplicate_ids_path)

    print(f"\n{'='*60}")
    print(f"Saved duplicate TMDB ID details to {duplicate_ids_path}")

    unique_tmdb_ids = (
        tmdb_duplicates_df
        .select("tmdbId")
        .unique()
        .to_series()
        .to_list()
    )
    
    tmdb_genres_df = asyncio.run(check_all_ids(unique_tmdb_ids))

    # join back to get all movieIds for each tmdbId to do comparison 
    full_comparison_df = (
        tmdb_duplicates_df
        .select(["tmdbId", "movieId"])
        .join(tmdb_genres_df.select(["tmdbId", "genres"]), on="tmdbId", how="left")
        .join(movies_df, on="movieId", how="left")
        .rename({"genres": "tmdb_genres", "genres_right": "dataset_genres"})
    )
    
    movies_to_remove_df, old_movies_ids, new_movie_ids = compare_genres(full_comparison_df, movies_df)

    remove_movies(
        movies_to_remove_df, 
        old_movies_ids, 
        new_movie_ids, 
        links_path, 
        movies_path, 
        ratings_path, 
        links_df, 
        movies_df, 
        ratings_df
    )