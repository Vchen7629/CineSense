import requests
import polars as pl
import aiohttp
import asyncio
import os
from typing import Optional, List, Union
import re
from dataclasses import dataclass, asdict

API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIwM2Q2YWFlZDhhZWQ0MWVjMGY4ZmVhM2MyZWYwNGU1ZCIsIm5iZiI6MTc1ODc3MzE3MC4yNDcsInN1YiI6IjY4ZDRiZmIyOTYxNzQwMTEyM2EyYmMyNCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.aDdNgN5KfMoSVfsPxuQrbsWPMXeVQDjU1GymrTmVNNc'
OMDB_API_KEY = 'e3c669f6'
OMDB_API_KEY2 = '62ba9d55'
headers = {'Authorization': f'Bearer {API_KEY}'}
current_dir = os.path.dirname(__file__)

# structure for a complete movie row in the csv
@dataclass
class MovieMetaData:
    id: str
    title: str
    vote_average: float  # Changed from vote_avg to match CSV
    vote_count: int
    status: str
    release_date: str
    revenue: int
    runtime: int
    budget: int
    imdb_id: str
    original_language: str
    original_title: str
    overview: str
    popularity: float
    tagline: str
    genres: str
    production_companies: str
    production_countries: str
    spoken_languages: str
    cast: str
    director: str
    director_of_photography: str
    writers: str
    producers: str
    music_composer: str
    imdb_rating: Optional[float] = 0.0
    imdb_votes: Optional[int] = 0
    poster_path: Optional[str] = ""

def handle_not_found(movie_id: str, imdbId: str, large_dataset: bool = False):
    if large_dataset:
        output_path = os.path.join(current_dir, '..', '..', 'datasets', 'output', 'not-found-imdb.csv')
    else:
        output_path = os.path.join(current_dir, '..', '..', 'datasets', 'output-small', 'not-found-imdb.csv')

     # Convert all values to strings, replacing None with ''
    row = [(str(movie_id), str(imdbId) if imdbId is not None else '')]

    new_row = pl.DataFrame(row, schema=['movieId', 'imdbId'], orient='row')

    # Read CSV with truncate_ragged_lines to handle malformed rows
    existing_df = pl.read_csv(output_path, truncate_ragged_lines=True)

    # Select only needed columns and cast to string
    existing_df = existing_df.select(['movieId', 'imdbId']).with_columns([
        pl.col('movieId').cast(pl.Utf8),
        pl.col('imdbId').cast(pl.Utf8),
    ])

    combined_df = pl.concat([existing_df, new_row], how='vertical')

    combined_df.write_csv(output_path)

# extract the year from text: 'Movie Name (1983)' -> '1983'
def extract_year(title: str) -> Optional[str]:
    match = re.search(r'\((\d{4})\)$', title.strip())
    return match.group(1) if match else None

# normalize title by removing punctuation and extra spaces
def normalize_title(title: str) -> str:
    # remove common punctuation and convert to lowercase
    normalized = title.lower()
    # remove punctuation like commas, periods, colons, hyphens, apostrophes
    for char in [',', '’', '…', '.', ':', '-', ''', ''', '!', '?']:
        normalized = normalized.replace(char, ' ')
    # collapse multiple spaces into one
    normalized = ' '.join(normalized.split())
    return normalized

# check if title returned in api res matches title in metadata csv
def titles_match(metadata_title: str, api_title: str) -> bool:
    metadata_clean = normalize_title(metadata_title)
    api_clean = normalize_title(api_title)

    # check if api title is contained in the title in metadata csv
    return api_clean in metadata_clean or metadata_clean in api_clean

# validate if api response matches the movie metadata
def validate_match(movie_id: str, title: str, year: str, api_title: str, api_ori_title: str, api_date: str) -> bool:
    if not api_date:
        return None
    
    # extract year from API Date (YYYY-MM-DD -> YYYY)
    api_year = api_date.replace('–', '-').split('-')[0].strip()

    # normalize year to string for comparison
    if not year:
        return None

    year_str = str(year)

    # check if titles match (either title or original_title)
    if not (titles_match(title, api_title) or titles_match(title, api_ori_title)):
        print(f"Title mismatch for {movie_id}: '{title}' vs '{api_title}' / '{api_ori_title}'")
        return False

    # check if years match (convert both to string for comparison)
    if year_str and api_year and year_str != api_year:
        print(f'Year mismatch for {movie_id}: {year_str} vs {api_year} (types: {type(year_str)}, {type(api_year)})')
        return False

    #print(f'Match for {movie_id}: {api_title} ({api_year})')
    return True

# handler function for http error handling
async def try_fetch_url(session, url: str, headers: dict) -> Optional[dict]:
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with session.get(url, headers=headers, timeout=timeout) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 404:
                return None 
            else:
                print(f'API returned status {resp.status} for {url}')
                return None
    except asyncio.TimeoutError:
        print(f'Timeout fetching {url}')
        return None
    except aiohttp.ClientError as e:
        print(f'Network error fetching {url}: {e}')
        return None

# async function for fetching tmdb id along with other movie info using TMDB api
async def find_by_id(session, imdbId: str):
    fetch_tmdb_id_url = f'https://api.themoviedb.org/3/find/tt{imdbId}?external_source=imdb_id'

    json_res = await try_fetch_url(session, fetch_tmdb_id_url, headers)

    # check movies
    if json_res.get('movie_results'):
        movie_details = json_res['movie_results'][0]
        # skip collections, only use actual movies
        if movie_details.get('media_type') == 'collection':
            print(f"Skipping collection for imdbId: {imdbId}")
            return None
        # early return if genres arent found for movie
        if not movie_details.get("genre_ids"):
            print(f"Imdb id found but no genre found for: {imdbId}")
            return None
        
        tmdb_id = movie_details['id']
        api_title = movie_details['title']
        original_title = movie_details['original_title']
        release_date = movie_details['release_date']
    else:
        print(f"imdbId not found using tmdb api for: {imdbId}")
        return None
    
    return tmdb_id, api_title, original_title, release_date

# normalize a field that can be a list or str in the api res
def normalize_details_fields(json_data, possible_keys: List[str], list_key_name: str, fallback: str):
    value = None
    for key in possible_keys:
        value = json_data.get(key)
        if value is not None:
            break
    
    if isinstance(value, list):
        return "|".join([item.get(list_key_name) for item in value if item.get(list_key_name)])
    elif isinstance(value, str):
        return value.replace(", ", "|")
    else:
        return fallback

# Normalize cast/crew fields that can be in array or string format.
def normalize_cast_fields(json_data, possible_keys: List, list_key_name: str, fallback: str,
                           job_filter=None, department_filter=None):
    value = None
    for key in possible_keys:
        value = json_data.get(key)
        if value is not None:
            break

    if isinstance(value, list):
        filtered_items = value

        # Filter by job titles (e.g., ["Director", "Series Director"])
        if job_filter:
            filtered_items = [
                item for item in filtered_items
                if item.get("job") in job_filter
                or any(j.get("job") in job_filter for j in item.get("jobs", []))
            ]

        # Filter by department (e.g., "Writing")
        if department_filter:
            filtered_items = [item for item in filtered_items if item.get("department") == department_filter]

        return "|".join([item.get(list_key_name) for item in filtered_items if item.get(list_key_name)]) or fallback

    elif isinstance(value, str):
        return value.replace(", ", "|")

    return fallback

# function for extracting movie/tvshow details
def extract_details(json_data, imdb_id) -> dict:
    return {
        "id": json_data.get("id") or 0,
        "title": json_data.get("title") 
              or "(no_title_provided)",
        "vote_average": json_data.get("vote_average") or 0.0,
        "vote_count": json_data.get("vote_count") or 0,
        "release_date": json_data.get("release_date") or "(no_release_date)",
        "status": json_data.get("status") or "(no_status)",
        "revenue": json_data.get("revenue") or 0,
        "runtime": json_data.get("runtime") or 0,
        "budget": json_data.get("budget", 0),
        "imdb_id": f"tt{imdb_id}",
        "original_language": json_data.get("original_language") or "(no_language)",
        "original_title": json_data.get("original_title") or "(no_original_title)",
        "overview": json_data.get("overview") or "(no_overview_found)",
        "popularity": json_data.get("popularity") or 0.0,
        "tagline": json_data.get("tagline") or "(no_tagline)",
        "genres": normalize_details_fields(
            json_data, 
            possible_keys=["Genre", "genres"], 
            list_key_name="name", 
            fallback="(no_genres_listed)"),
        "production_companies": normalize_details_fields(
            json_data, 
            possible_keys=["Production", "production_companies"], 
            list_key_name="name", 
            fallback="(no_production_companies)"),
        "production_countries": normalize_details_fields(
            json_data, 
            possible_keys=["Country", "production_countries"], 
            list_key_name="name", 
            fallback="(no_countries_listed)"),
        "spoken_languages": normalize_details_fields(
            json_data, 
            possible_keys=["Language", "spoken_languages"], 
            list_key_name="english_name", 
            fallback="(no_languages_listed)"),
        "poster_path": json_data.get("poster_path")
                    or json_data.get("Poster")
                    or "(no_poster_path)"
    }

# function for extracting movie/tvshow credits
def extract_credits(json_data) -> dict:
    return {
        "cast": normalize_cast_fields(
            json_data,
            possible_keys=["cast", "Actors"],
            list_key_name="name",
            fallback="(no-cast)"
        ),
        "director": normalize_cast_fields(
            json_data,
            possible_keys=["crew", "Director"],
            list_key_name="name",
            fallback="(no-director)",
            job_filter=["Director", "Series Director"]
        ),
        "director_of_photography": normalize_cast_fields(
            json_data,
            possible_keys=["crew"],
            list_key_name="name",
            fallback="(no-director-of-photography)",
            job_filter=["Director of Photography"]
        ),
        "writers": normalize_cast_fields(
            json_data,
            possible_keys=["crew", "Writer"],
            list_key_name="name",
            fallback="(no-writers)",
            department_filter="Writing"
        ),
        "producers": normalize_cast_fields(
            json_data,
            possible_keys=["crew"],
            list_key_name="name",
            fallback="(no-producer)",
            job_filter=["Producer", "Executive Producer"]
        ),
        "music_composer": normalize_cast_fields(
            json_data,
            possible_keys=["crew"],
            list_key_name="name",
            fallback="(no-music-composer)",
            job_filter=["Original Music Composer"]
        ),
    }

# async function for fetching the json object containing all the movie/tvshow details
# using the tmdb api
async def fetch_tmdb_details_json(session, tmdb_id: str) -> dict:
    fetch_movie_metadata_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}?language=en-US'
    
    result = await try_fetch_url(session, fetch_movie_metadata_url, headers)

    return result

# async function for fetching the json object containing all the movie/tvshow details
# using the tmdb api
async def fetch_tmdb_credits_json(session, tmdb_id: str) -> dict:
    fetch_movie_credits_url = f'https://api.themoviedb.org/3/movie/{tmdb_id}/credits?language=en-US'

    result = await try_fetch_url(session, fetch_movie_credits_url, headers)

    return result


async def fetch_complete_movie_metadata(session, movieId: str, imdb_id: str, title: str, year: str) -> Optional[MovieMetaData]:
    try:
        # find the movie/tvshow with tmdb api with imdbId
        result = await find_by_id(session, imdb_id)
        if not result:
            handle_not_found(movieId, imdb_id)
            print(f"TMDB ID not found for movie: {movieId} with imdb_id: {imdb_id}")

        # tmdb api does return value
        tmdb_id, api_title, original_title, release_date = result

        # validate that the movie/tvshow returned by api matches the one we are updating for
        matches = validate_match(movieId, title, year, api_title, original_title, release_date)
        if not matches:
            print(f"movie: {movieId} with imdb_id: {imdb_id} doesnt match")
            handle_not_found(movieId, imdb_id)
            return None

        # fetch the json containing all of the details for tvshows/movies
        details_json = await fetch_tmdb_details_json(session, tmdb_id)
        if not details_json:
            print(f"details not found for movie: {movieId} tmdbId: {tmdb_id}")
            return None

        # fetch the json containing all of the credits for tvshows/movies
        credits_json = await fetch_tmdb_credits_json(session, tmdb_id)
        if not credits_json:
            print(f"credits not found for movie: {movieId} tmdbId: {tmdb_id}")
            return None

        # extract relevant fields from the json
        details_data = extract_details(details_json, imdb_id)
        credits_data = extract_credits(credits_json)

        # merge and create structured object
        return MovieMetaData(**{**details_data, **credits_data})
    
    except Exception as e:
        print(f"Error fetching {imdb_id}: {e}")
        return None

async def fetch_all(batch_size: int = 20, large_dataset: bool = False):
    if large_dataset:
        input_missing_path = os.path.join(current_dir, '..', '..', 'datasets', 'output', 'missing-metadata.csv')
    else: 
        input_missing_path = os.path.join(current_dir, '..', '..', 'datasets', 'output-small', 'missing-metadata.csv')
    # Read imdbId as string to preserve leading zeros
    missing_df = pl.read_csv(input_missing_path, dtypes={'imdbId': pl.Utf8}, truncate_ragged_lines=True)

    async with aiohttp.ClientSession() as session:
        tasks = []
        results = []

        for row in missing_df.iter_rows(named=True):
            tasks.append(fetch_complete_movie_metadata(session, row['movieId'], row['imdbId'], row['title'], row['year']))

            if len(tasks) >= batch_size:
                results += await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(1)

        if tasks:
            results += await asyncio.gather(*tasks)

        return results


def run_fetch_movies(large_dataset: bool = False):
    output_update_path = os.path.join(current_dir, '..', '..', 'datasets', 'metadata', 'TMDB_all_movies_cleaned.csv')

    print('Fetching missing rows')
    results = asyncio.run(fetch_all(large_dataset=large_dataset))

    # filtering out none values
    valid_results = [asdict(r) for r in results if r is not None]

    print(f'\nGot {len(valid_results)} valid results')

    # append the new rows to the existing csv
    if valid_results:
        new_df = pl.DataFrame(valid_results)
    
        existing_df = pl.read_csv(output_update_path)

        for col in new_df.columns:
            if col in existing_df.columns:
                new_df = new_df.with_columns(
                    pl.col(col).cast(existing_df[col].dtype)
                )

        updated_df = existing_df.join(
            new_df,
            on=["imdb_id"],
            how="left"
        )

        coalesce_columns = []
        columns_to_drop = []

        for col in new_df.columns:
            if col != "imdb_id":
                new_col_name = f"{col}_right"
                # Check if column is string type before comparing to empty string
                if new_df[col].dtype == pl.Utf8:
                    coalesce_columns.append(
                        pl.when((pl.col(col).is_null()) | (pl.col(col) == ""))
                        .then(pl.col(new_col_name))
                        .otherwise(pl.col(col))
                        .alias(col)
                    )
                else:
                    # For numeric columns, only check for null
                    coalesce_columns.append(
                        pl.when(pl.col(col).is_null())
                        .then(pl.col(new_col_name))
                        .otherwise(pl.col(col))
                        .alias(col)
                    )
                columns_to_drop.append(new_col_name)
        
        updated_df = updated_df.with_columns(coalesce_columns).drop(columns_to_drop)

        inserts = new_df.join(
            existing_df.select(["imdb_id"]),
            on=["imdb_id"],
            how="anti"
        )

        combined_df = pl.concat([updated_df, inserts], how="vertical")

        combined_df.write_csv(output_update_path)

        print('Done! now run movie_dataset.py again to add the new rows to the movie-metadata csv')
    else:
        print("No valid results to write")


