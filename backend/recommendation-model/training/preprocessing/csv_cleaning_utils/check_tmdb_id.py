import os
import asyncio
import aiohttp
import polars as pl
from dotenv import load_dotenv
import re

current_dir = os.path.dirname(__file__)

# Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# extract year from movie title if its in the format 'Movie Name (1995)'
def extract_year_from_title(title: str) -> int | None:
    match = re.search(r'\((\d{4})\)$', title)
    return int(match.group(1)) if match else None

# fetch movie details from TMDB API by ID
async def fetch_movie_from_tmdb(session: aiohttp.ClientSession, tmdb_id: int, semaphore: asyncio.Semaphore):
    async with semaphore:
        url = f"{TMDB_BASE_URL}/movie/{tmdb_id}?language=en-US"
        headers = {'Authorization': f'Bearer {TMDB_API_KEY}'}

        try:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'tmdb_id': tmdb_id,
                        'title': data.get('title', ''),
                        'release_date': data.get('release_date', ''),
                        'year': int(data['release_date'][:4]) if data.get('release_date') else None,
                        'found': True
                    }
                elif response.status == 404:
                    return {
                        'tmdb_id': tmdb_id,
                        'title': 'NOT FOUND',
                        'release_date': '',
                        'year': None,
                        'found': False
                    }
                else:
                    print(f"Error fetching TMDB ID {tmdb_id}: {response.status}")
                    return None
        except Exception as e:
            print(f"Exception fetching TMDB ID {tmdb_id}: {e}")
            return None

async def verify_all_movies(movies_df: pl.DataFrame, links_df: pl.DataFrame, max_concurrent: int = 40):
    """
    Verify all movies by comparing MovieLens data with TMDB API.

    Args:
        movies_df: DataFrame with MovieLens movies
        links_df: DataFrame with TMDB IDs
        max_concurrent: Max concurrent requests (TMDB allows ~40/10s)
    """
    # Join movies with links to get TMDB IDs
    movies_with_tmdb = movies_df.join(links_df.select(["movieId", "tmdbId"]), on="movieId", how="left")

    # Filter to only movies with TMDB IDs
    movies_with_tmdb = movies_with_tmdb.filter(pl.col("tmdbId").is_not_null())

    print(f"Verifying {len(movies_with_tmdb)} movies with TMDB IDs...")

    # Extract years from titles
    movies_with_tmdb = movies_with_tmdb.with_columns([
        pl.col("title").map_elements(extract_year_from_title, return_dtype=pl.Int64).alias("movielens_year"),
        pl.col("title").map_elements(lambda t: t.rsplit(' (', 1)[0] if extract_year_from_title(t) else t, return_dtype=pl.Utf8).alias("clean_title")
    ])

    # Fetch from TMDB API
    semaphore = asyncio.Semaphore(max_concurrent)

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_movie_from_tmdb(session, int(row['tmdbId']), semaphore)
            for row in movies_with_tmdb.iter_rows(named=True)
        ]

        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            if result:
                results.append(result)

            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1}/{len(tasks)} movies...")

        print(f"Completed fetching {len(results)} movies from TMDB API")

    # Convert results to DataFrame
    tmdb_results_df = pl.DataFrame(results)

    # Join with original data
    comparison_df = movies_with_tmdb.join(
        tmdb_results_df,
        left_on="tmdbId",
        right_on="tmdb_id",
        how="left"
    )

    # Find mismatches
    mismatches = comparison_df.filter(
        (~pl.col("found")) |  # Not found in TMDB
        (pl.col("clean_title").str.to_lowercase() != pl.col("title").str.to_lowercase()) |  # Title mismatch
        ((pl.col("movielens_year").is_not_null()) & (pl.col("year").is_not_null()) & (pl.col("movielens_year") != pl.col("year")))  # Year mismatch
    ).select([
        pl.col("movieId"),
        pl.col("tmdbId"),
        pl.col("clean_title").alias("movielens_title"),
        pl.col("movielens_year"),
        pl.col("title").alias("tmdb_title"),
        pl.col("year").alias("tmdb_year"),
        pl.when(~pl.col("found"))
            .then(pl.lit("TMDB ID not found (404)"))
            .when(pl.col("clean_title").str.to_lowercase() != pl.col("title").str.to_lowercase())
            .then(pl.lit("Title mismatch"))
            .otherwise(pl.lit("Year mismatch"))
            .alias("issue")
    ])

    return mismatches

# check tmdb ids in links.csv match actual movie titles and years, save mismatches to csv
def check_tmdb_ids(movies_path: str, links_path: str, mismatched_id_path: str):
    # Load data
    movies_df = pl.read_csv(movies_path)
    links_df = pl.read_csv(links_path)

    print(f"Loaded {len(movies_df)} movies from {movies_path}")
    print(f"Loaded {len(links_df)} links from {links_path}")

    # Run async verification
    mismatches = asyncio.run(verify_all_movies(movies_df, links_df))

    # Save results
    if len(mismatches) > 0:
        mismatches.write_csv(mismatched_id_path)
        print(f"\n{'='*60}")
        print(f"Found {len(mismatches)} mismatches!")
        print(f"Saved to {mismatched_id_path}")
        print(f"\nSample mismatches:")
        print(mismatches.head(10))
    else:
        print(f"\n{'='*60}")
        print("No mismatches found! All TMDB IDs are correct.")
