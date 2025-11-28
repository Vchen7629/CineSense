import polars as pl
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
from ..shared.extract_year import extract_year_from_title, extract_title_without_year

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"


async def lookup_tmdb_from_imdb(session: aiohttp.ClientSession, movie_id: int, imdb_id: str, movie_title: str, movie_year: int | None, semaphore: asyncio.Semaphore):
    """
    Lookup TMDB ID via IMDB ID for both movies and TV shows.
    Returns dict with tmdbId and media_type if found, None otherwise.
    """
    async with semaphore:
        if not imdb_id:
            return None

        # Format IMDB ID: add tt prefix and zero-pad to 7 digits
        imdb_id_clean = str(imdb_id).strip()
        imdb_id_formatted = f"tt{imdb_id_clean.zfill(7)}"

        url = f"{TMDB_BASE_URL}/find/{imdb_id_formatted}?external_source=imdb_id"
        headers = {'Authorization': f'Bearer {TMDB_API_KEY}'}

        try:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    return None

                data = await response.json()

                # Extract clean title without year from MovieLens title
                clean_movie_title = extract_title_without_year(movie_title)

                # Check movie results first
                if data.get('movie_results') and len(data['movie_results']) > 0:
                    movie = data['movie_results'][0]
                    tmdb_id = movie.get('id')
                    api_title = movie.get('title', '')
                    release_date = movie.get('release_date', '')
                    api_year = int(release_date[:4]) if release_date else None

                    # Validate title match (case-insensitive)
                    title_match = clean_movie_title.lower() == api_title.lower()

                    # Validate year match (allow None)
                    year_match = (movie_year is None or api_year is None or movie_year == api_year)

                    if title_match and year_match:
                        print(f"Movie {movie_id}: Found tmdbId {tmdb_id} for '{movie_title}' (imdbId: {imdb_id_formatted}) [MOVIE]")
                        return {'tmdbId': tmdb_id, 'media_type': 'movie'}
                    else:
                        mismatch_reason = []
                        if not title_match:
                            mismatch_reason.append(f"title mismatch: '{clean_movie_title}' vs '{api_title}'")
                        if not year_match:
                            mismatch_reason.append(f"year mismatch: {movie_year} vs {api_year}")
                        print(f"Movie {movie_id}: Validation failed - {', '.join(mismatch_reason)} [MOVIE]")
                        return None

                # Check TV show results
                elif data.get('tv_results') and len(data['tv_results']) > 0:
                    tv_show = data['tv_results'][0]
                    tmdb_id = tv_show.get('id')
                    api_title = tv_show.get('name', '')
                    first_air_date = tv_show.get('first_air_date', '')
                    api_year = int(first_air_date[:4]) if first_air_date else None

                    # Validate title match (case-insensitive)
                    title_match = clean_movie_title.lower() == api_title.lower()

                    # Validate year match (allow None)
                    year_match = (movie_year is None or api_year is None or movie_year == api_year)

                    if title_match and year_match:
                        print(f"Movie {movie_id}: Found tmdbId {tmdb_id} for '{movie_title}' (imdbId: {imdb_id_formatted}) [TV SHOW]")
                        return {'tmdbId': tmdb_id, 'media_type': 'tv'}
                    else:
                        mismatch_reason = []
                        if not title_match:
                            mismatch_reason.append(f"title mismatch: '{clean_movie_title}' vs '{api_title}'")
                        if not year_match:
                            mismatch_reason.append(f"year mismatch: {movie_year} vs {api_year}")
                        print(f"Movie {movie_id}: Validation failed - {', '.join(mismatch_reason)} [TV SHOW]")
                        return None

                else:
                    return None

        except Exception as e:
            print(f"Movie {movie_id}: Exception during lookup - {str(e)}")
            return None


async def fill_missing_tmdb_ids_async(movies_df: pl.DataFrame, links_df: pl.DataFrame, null_tmdb_path: str, max_concurrent: int = 40):
    """
    Find and fill missing tmdbIds in links.csv by looking them up via IMDB IDs.
    Works for both movies and TV shows.
    Saves remaining null tmdbIds to null_tmdb_id.csv with reasons.
    """
    # Join movies and links to get movie titles
    joined_df = links_df.join(movies_df, on="movieId", how="inner")

    # Extract year from title
    joined_df = joined_df.with_columns([
        pl.col("title").map_elements(extract_year_from_title, return_dtype=pl.Int64).alias("movielens_year")
    ])

    # Find rows with null tmdbId
    missing_tmdb_df = joined_df.filter(pl.col("tmdbId").is_null())

    if len(missing_tmdb_df) == 0:
        # Write empty file with headers
        pl.DataFrame({
            'movieId': [],
            'imdbId': [],
            'title': [],
            'reason': []
        }).write_csv(null_tmdb_path)
        return links_df

    # Lookup tmdbIds via IMDB API
    semaphore = asyncio.Semaphore(max_concurrent)

    async with aiohttp.ClientSession() as session:
        tasks = [
            lookup_tmdb_from_imdb(
                session,
                row['movieId'],
                str(row['imdbId']),
                row['title'],
                row['movielens_year'],
                semaphore
            )
            for row in missing_tmdb_df.iter_rows(named=True)
        ]
        results = await asyncio.gather(*tasks)

    # Add results to dataframe
    missing_tmdb_df = missing_tmdb_df.with_columns([
        pl.Series("lookup_result", results)
    ])

    # Separate successful and failed lookups
    successful_df = missing_tmdb_df.filter(pl.col("lookup_result").is_not_null())
    failed_df = missing_tmdb_df.filter(pl.col("lookup_result").is_null())

    # Update links_df with successful tmdbIds
    if len(successful_df) > 0:
        # Extract tmdbId from result dict
        tmdb_mapping = {
            row['movieId']: row['lookup_result']['tmdbId']
            for row in successful_df.iter_rows(named=True)
        }

        links_df = links_df.with_columns([
            pl.when(pl.col("movieId").is_in(list(tmdb_mapping.keys())))
            .then(pl.col("movieId").replace(tmdb_mapping, default=None))
            .otherwise(pl.col("tmdbId"))
            .alias("tmdbId")
        ])

    # Save failed lookups to null_tmdb_id.csv
    if len(failed_df) > 0:
        null_tmdb_df = failed_df.select([
            pl.col("movieId"),
            pl.col("imdbId"),
            pl.col("title"),
            pl.lit("IMDB lookup failed or validation failed").alias("reason")
        ])
        null_tmdb_df.write_csv(null_tmdb_path)
    else:
        # Write empty file with headers
        pl.DataFrame({
            'movieId': [],
            'imdbId': [],
            'title': [],
            'reason': []
        }).write_csv(null_tmdb_path)

    return links_df


def fill_missing_tmdb_ids(movies_path: str, links_path: str, null_tmdb_path: str):
    """
    Main function to fill missing tmdbIds in links.csv.
    Reads movies.csv and links.csv, looks up missing tmdbIds, and updates links.csv.
    Works for both movies and TV shows.
    Saves remaining null tmdbIds to null_tmdb_id.csv.
    """
    print("\n" + "="*60)
    print("FILLING MISSING TMDB IDs")
    print("="*60)

    # Read files
    movies_df = pl.read_csv(movies_path)
    links_df = pl.read_csv(links_path)

    # Fill missing tmdbIds
    updated_links_df = asyncio.run(fill_missing_tmdb_ids_async(movies_df, links_df, null_tmdb_path))

    # Write updated links.csv
    updated_links_df.write_csv(links_path)
    print("="*60 + "\n")
