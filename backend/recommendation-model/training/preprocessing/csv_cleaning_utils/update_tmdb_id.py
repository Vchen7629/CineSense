import os
import asyncio
import aiohttp
import polars as pl
from dotenv import load_dotenv
from shared.extract_year import extract_title_without_year, extract_year_from_title

current_dir = os.path.dirname(__file__)

# Load environment variables
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

async def verify_tmdb_id_direct(session: aiohttp.ClientSession, tmdb_id: int, semaphore: asyncio.Semaphore):
    """Verify a TMDB ID directly by fetching movie details."""
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
                else:
                    return {'tmdb_id': tmdb_id, 'found': False}
        except Exception:
            return {'tmdb_id': tmdb_id, 'found': False}

async def lookup_tmdb_from_imdb(session: aiohttp.ClientSession, movie_id: int, imdb_id: str, tmdb_id: int | None, movie_title: str, movie_year: int | None, semaphore: asyncio.Semaphore):
    """
    Lookup movie via IMDB ID using TMDB Find API.
    Returns complete information about the match status.
    """
    async with semaphore:
        # Strategy: Try IMDB ID lookup first, fall back to TMDB ID verification if IMDB fails
        imdb_result = None
        tmdb_direct_result = None

        # Try IMDB ID lookup
        if imdb_id:
            imdb_id_clean = str(imdb_id).replace('tt', '').strip()
            imdb_id_formatted = f"tt{imdb_id_clean.zfill(7)}"

            url = f"{TMDB_BASE_URL}/find/{imdb_id_formatted}?external_source=imdb_id"
            headers = {'Authorization': f'Bearer {TMDB_API_KEY}'}

            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        imdb_result = await response.json()
            except Exception:
                pass

        # If IMDB lookup failed and we have a TMDB ID, verify it directly
        if (not imdb_result or (not imdb_result.get('movie_results') and not imdb_result.get('tv_results'))) and tmdb_id:
            tmdb_direct_result = await verify_tmdb_id_direct(session, tmdb_id, semaphore)

        # Process results
        try:
            # Check IMDB results first
            if imdb_result:
                data = imdb_result

                # Check if we found movie results (not TV shows)
                if data.get('movie_results') and len(data['movie_results']) > 0:
                    movie = data['movie_results'][0]
                    tmdb_title = movie.get('title', '')
                    release_date = movie.get('release_date', '')
                    tmdb_year = int(release_date[:4]) if release_date else None
                    tmdb_id = movie.get('id')

                    # Check if title and year match
                    title_match = movie_title.lower() == tmdb_title.lower()
                    year_match = (movie_year is None or tmdb_year is None or movie_year == tmdb_year)

                    # Determine issue
                    if title_match and year_match:
                        issue = None  # Perfect match
                    elif not title_match and not year_match:
                        issue = "Title and Year mismatch"
                    elif not title_match:
                        issue = "Title mismatch"
                    else:
                        issue = "Year mismatch"

                    return {
                        'movieId': movie_id,
                        'imdbId': imdb_id,
                        'tmdbId': tmdb_id,
                        'movielens_title': movie_title,
                        'movielens_year': movie_year,
                        'api_title': tmdb_title,
                        'api_year': tmdb_year,
                        'issue': issue
                    }

                # Check for TV shows
                elif data.get('tv_results') and len(data['tv_results']) > 0:
                    tv_show = data['tv_results'][0]
                    return {
                        'movieId': movie_id,
                        'imdbId': imdb_id,
                        'tmdbId': None,
                        'movielens_title': movie_title,
                        'movielens_year': movie_year,
                        'api_title': tv_show.get('name', ''),
                        'api_year': int(tv_show.get('first_air_date', '')[:4]) if tv_show.get('first_air_date') else None,
                        'issue': "TV Show"
                    }

                # Not found via IMDB - try TMDB direct fallback
                elif tmdb_direct_result and tmdb_direct_result.get('found'):
                    # IMDB ID is outdated/wrong, but TMDB ID is valid
                    tmdb_title = tmdb_direct_result.get('title', '')
                    tmdb_year = tmdb_direct_result.get('year')

                    title_match = movie_title.lower() == tmdb_title.lower()
                    year_match = (movie_year is None or tmdb_year is None or movie_year == tmdb_year)

                    if title_match and year_match:
                        issue = "IMDB ID outdated (verified via TMDB ID)"
                    elif not title_match and not year_match:
                        issue = "IMDB ID outdated + Title and Year mismatch"
                    elif not title_match:
                        issue = "IMDB ID outdated + Title mismatch"
                    else:
                        issue = "IMDB ID outdated + Year mismatch"

                    return {
                        'movieId': movie_id,
                        'imdbId': imdb_id,
                        'tmdbId': tmdb_id,  # Keep existing TMDB ID
                        'movielens_title': movie_title,
                        'movielens_year': movie_year,
                        'api_title': tmdb_title,
                        'api_year': tmdb_year,
                        'issue': issue
                    }
                else:
                    return {
                        'movieId': movie_id,
                        'imdbId': imdb_id,
                        'tmdbId': None,
                        'movielens_title': movie_title,
                        'movielens_year': movie_year,
                        'api_title': '',
                        'api_year': None,
                        'issue': "404 Not Found"
                    }
        except Exception as e:
            print(f"Exception looking up IMDB ID {imdb_id_formatted}: {e}")
            return {
                'movieId': movie_id,
                'imdbId': imdb_id,
                'tmdbId': None,
                'movielens_title': movie_title,
                'movielens_year': movie_year,
                'api_title': '',
                'api_year': None,
                'issue': f"Exception: {str(e)}"
            }

async def lookup_all_imdb_ids(movies_df: pl.DataFrame, max_concurrent: int = 40):
    """Lookup all movies via IMDB IDs."""
    semaphore = asyncio.Semaphore(max_concurrent)

    print(f"Looking up {len(movies_df)} movies via IMDB IDs...")

    async with aiohttp.ClientSession() as session:
        tasks = [
            lookup_tmdb_from_imdb(
                session,
                row['movieId'],
                str(row['imdbId']),
                row['tmdbId'],
                row['clean_title'],
                row['movielens_year'],
                semaphore
            )
            for row in movies_df.iter_rows(named=True)
        ]

        results = []
        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            if result:
                results.append(result)

            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1}/{len(tasks)} IMDB IDs...")

        print(f"Completed lookup for {len(results)} IMDB IDs")

    return pl.DataFrame(results)

def update_tmdb_id(movies_path: str, links_path: str, mismatches_path: str):
    """
    Check all movies via IMDB ID lookup.
    - Updates links.csv with correct TMDB IDs where title and year match
    - Writes mismatches to imdb_mismatches.csv for manual review
    """
    # Load data
    movies_df = pl.read_csv(movies_path)
    links_df = pl.read_csv(links_path)

    print(f"Loaded {len(movies_df)} movies from {movies_path}")
    print(f"Loaded {len(links_df)} links from {links_path}")

    # Join movies with links
    movies_with_links = movies_df.join(
        links_df.select(["movieId", "tmdbId", "imdbId"]),
        on="movieId",
        how="left"
    )

    # Find movies that have IMDB IDs
    movies_to_check = movies_with_links.filter(
        pl.col("imdbId").is_not_null()
    )

    if len(movies_to_check) == 0:
        print("No movies with IMDB IDs found")
        return

    print(f"\nFound {len(movies_to_check)} movies with IMDB IDs")

    # Extract clean titles and years
    movies_to_check = movies_to_check.with_columns([
        pl.col("title").map_elements(extract_year_from_title, return_dtype=pl.Int64).alias("movielens_year"),
        pl.col("title").map_elements(extract_title_without_year, return_dtype=pl.Utf8).alias("clean_title")
    ])

    # Lookup all movies via IMDB IDs
    results_df = asyncio.run(lookup_all_imdb_ids(movies_to_check))

    # Separate perfect matches from mismatches
    perfect_matches = results_df.filter(pl.col("issue").is_null())
    mismatches = results_df.filter(pl.col("issue").is_not_null())

    print(f"\n{'='*60}")
    print(f"Results:")
    print(f"  Perfect matches (title & year): {len(perfect_matches)}")
    print(f"  Mismatches: {len(mismatches)}")

    if len(mismatches) > 0:
        # Show breakdown of issues
        issue_counts = mismatches.group_by("issue").agg(pl.count()).sort("count", descending=True)
        print(f"\nMismatch breakdown:")
        for row in issue_counts.iter_rows(named=True):
            print(f"  {row['issue']}: {row['count']}")

        # Write mismatches to CSV
        mismatches.write_csv(mismatches_path)
        print(f"\nWrote {len(mismatches)} mismatches to {mismatches_path}")

    # Update links.csv with correct TMDB IDs from perfect matches
    if len(perfect_matches) > 0:
        # Create mapping of movieId -> correct TMDB ID
        update_mapping = perfect_matches.select([
            pl.col("movieId"),
            pl.col("tmdbId").alias("tmdbId_correct")
        ])

        # Join and compare
        links_with_correct = links_df.join(
            update_mapping,
            on="movieId",
            how="left"
        )

        # Count updates needed
        needs_update = links_with_correct.filter(
            pl.col("tmdbId_correct").is_not_null() &
            (
                pl.col("tmdbId").is_null() |
                (pl.col("tmdbId") != pl.col("tmdbId_correct"))
            )
        )

        print(f"\nUpdating {len(needs_update)} TMDB IDs in links.csv")
        print(f"  Missing TMDB ID: {needs_update.filter(pl.col('tmdbId').is_null()).height}")
        print(f"  Outdated TMDB ID: {needs_update.filter(pl.col('tmdbId').is_not_null()).height}")

        # Update links with correct TMDB IDs
        updated_links = links_with_correct.with_columns([
            pl.coalesce([pl.col("tmdbId_correct"), pl.col("tmdbId")]).alias("tmdbId")
        ]).select(links_df.columns)

        # Write back to CSV
        updated_links.write_csv(links_path)
        print(f"Updated {links_path}")
    else:
        print("\nNo perfect matches found - links.csv not updated")
