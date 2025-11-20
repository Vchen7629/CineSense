import os
import asyncio
import aiohttp
import polars as pl
from dotenv import load_dotenv

current_dir = os.path.dirname(__file__)

# Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def check_media_type(session: aiohttp.ClientSession, tmdb_id: int, semaphore: asyncio.Semaphore):
    """Check if TMDB ID is a movie or TV show."""
    async with semaphore:
        headers = {'Authorization': f'Bearer {TMDB_API_KEY}'}

        movie_url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?language=en-US"
        tv_url = f"{TMDB_BASE_URL}/tv/{tmdb_id}?language=en-US"

        results = []

        try:
            # Check BOTH movie and TV endpoints
            async with session.get(movie_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results.append({
                        'tmdb_id': tmdb_id,
                        'media_type': 'movie',
                        'title': data.get('title', ''),
                        'release_date': data.get('release_date', ''),
                    })

            async with session.get(tv_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results.append({
                        'tmdb_id': tmdb_id,
                        'media_type': 'tv',
                        'title': data.get('name', ''),
                        'release_date': data.get('first_air_date', ''),
                    })

            return results  # Could be empty, one result, or TWO results (both movie and TV)

        except Exception as e:
            print(f"Exception checking TMDB ID {tmdb_id}: {e}")
            return []

async def check_all_duplicates(duplicate_ids: list, max_concurrent: int = 40):
    """Check all duplicate TMDB IDs to determine their media type."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async with aiohttp.ClientSession() as session:
        tasks = [
            check_media_type(session, tmdb_id, semaphore)
            for tmdb_id in duplicate_ids
        ]

        all_results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result_list = await coro
            if result_list:
                # Each call can return multiple results (movie AND tv)
                all_results.extend(result_list)

            if (i + 1) % 10 == 0:
                print(f"Checked {i + 1}/{len(tasks)} duplicate IDs...")

        print(f"Completed checking - found {len(all_results)} total entries")

    return pl.DataFrame(all_results)

# find duplicate TMDB ids in links.csv and identify which are tv shows to save to the duplicate csv
def find_duplicate_tmdb_ids(links_path: str, movies_path: str, duplicate_ids_path: str):
    """
    Find duplicate TMDB IDs in links.csv and identify which are TV shows.
    Saves results to duplicate_tmdb_ids.csv with media type information.
    """
    # Load data
    links_df = pl.read_csv(links_path)
    movies_df = pl.read_csv(movies_path)

    print(f"Loaded {len(links_df)} links")

    # Find duplicate TMDB IDs
    tmdb_counts = links_df.group_by("tmdbId").agg([
        pl.count("movieId").alias("count"),
        pl.col("movieId").alias("movieIds")
    ]).filter(pl.col("count") > 1).sort("count", descending=True)

    if len(tmdb_counts) == 0:
        print("No duplicate TMDB IDs found!")
        return

    print(f"\nFound {len(tmdb_counts)} duplicate TMDB IDs")
    print(f"Total movies affected: {tmdb_counts['count'].sum()}")
    print("\nTop duplicates:")
    print(tmdb_counts.head(10))

    # Get ALL movies with duplicate TMDB IDs (not just unique TMDB IDs)
    # We need to check each movie individually by TMDB ID
    movies_with_dup_tmdb = links_df.filter(
        pl.col("tmdbId").is_in(tmdb_counts["tmdbId"])
    )

    print(f"\nFound {len(movies_with_dup_tmdb)} total movies with duplicate TMDB IDs")
    print(f"Checking each one via API...")

    # Check each movie's TMDB ID (yes, we'll check same TMDB ID multiple times)
    # This is necessary because we need to see which MovieLens entry is wrong
    duplicate_ids = movies_with_dup_tmdb["tmdbId"].to_list()

    results_df = asyncio.run(check_all_duplicates(list(set(duplicate_ids))))

    # Filter results to only TV shows
    tv_shows_only = results_df.filter(pl.col("media_type") == "tv")

    # Join with MovieLens data to get which movieIds have TV show TMDB IDs
    tv_entries = movies_with_dup_tmdb.join(
        movies_df.select(["movieId", "title"]),
        on="movieId",
        how="left"
    ).join(
        tv_shows_only,
        left_on="tmdbId",
        right_on="tmdb_id",
        how="inner"  # Only keep entries that are TV shows
    ).select([
        "movieId",
        "tmdbId",
        "imdbId",
        pl.col("title").alias("movielens_title"),
        pl.col("title_right").alias("tmdb_title"),
        "media_type",
        "release_date"
    ])

    # Save only TV show entries
    tv_entries.write_csv(duplicate_ids_path)

    print(f"\n{'='*60}")
    print(f"Saved duplicate TMDB ID details to {duplicate_ids_path}")

    # Summary statistics
    print(f"\nSummary:")
    print(f"  Total TV show entries found: {len(tv_entries)}")
    print(f"  Unique TMDB IDs that are TV shows: {tv_entries['tmdbId'].n_unique()}")

    if len(tv_entries) > 0:
        print(f"\n⚠️  MovieIDs to remove from movies.csv (they are TV shows):")
        print(tv_entries.select(["movieId", "tmdbId", "movielens_title", "tmdb_title"]).sort("tmdbId"))

