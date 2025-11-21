import polars as pl
import re

def titles_have_common_word(title1: str, title2: str) -> bool:
    """
    Check if two titles share at least one significant word.
    Ignores common words like 'the', 'a', 'an', etc.
    """
    if not title1 or not title2:
        return False

    # Common words to ignore
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

    # Extract words (lowercase, alphanumeric only)
    words1 = set(re.findall(r'\b\w+\b', title1.lower()))
    words2 = set(re.findall(r'\b\w+\b', title2.lower()))

    # Remove stop words
    words1 = words1 - stop_words
    words2 = words2 - stop_words

    # Check if they share at least one word
    return len(words1 & words2) > 0

def fix_movie_mismatches(movies_path: str, mismatches_path: str):
    """
    Update movies.csv with correct titles and years from imdb_mismatches.csv.
    - For Title mismatch: Replace title with API title + year (only if titles share common words)
    - For Year mismatch: Replace year in title with correct API year
    - For Title and Year mismatch: Replace both if titles share common words
    """
    # Load data
    movies_df = pl.read_csv(movies_path)
    mismatches_df = pl.read_csv(mismatches_path)

    print(f"Loaded {len(movies_df)} movies from {movies_path}")
    print(f"Loaded {len(mismatches_df)} mismatches from {mismatches_path}")

    if len(mismatches_df) == 0:
        print("No mismatches to fix")
        return

    # Filter for fixable issues (title/year mismatches only)
    fixable_issues = [
        "Title mismatch",
        "Year mismatch",
        "Title and Year mismatch"
    ]

    fixable_mismatches = mismatches_df.filter(
        pl.col("issue").is_in(fixable_issues)
    )

    if len(fixable_mismatches) == 0:
        print("No fixable title/year mismatches found")
        return

    print(f"\nFound {len(fixable_mismatches)} fixable mismatches:")
    issue_counts = fixable_mismatches.group_by("issue").agg(pl.count()).sort("count", descending=True)
    for row in issue_counts.iter_rows(named=True):
        print(f"  {row['issue']}: {row['count']}")

    # Create corrected titles
    corrections = []
    skipped = []

    for row in fixable_mismatches.iter_rows(named=True):
        movie_id = row['movieId']
        issue = row['issue']
        movielens_title = row['movielens_title']
        api_title = row['api_title']
        api_year = row['api_year']

        # Check if titles share common words (for title mismatches)
        if "Title" in issue:
            if not titles_have_common_word(movielens_title, api_title):
                skipped.append({
                    'movieId': movie_id,
                    'reason': 'No common words',
                    'movielens_title': movielens_title,
                    'api_title': api_title
                })
                continue

        # Create corrected title
        if api_year:
            corrected_title = f"{api_title} ({api_year})"
        else:
            corrected_title = api_title

        corrections.append({
            'movieId': movie_id,
            'corrected_title': corrected_title,
            'original_title': movielens_title,
            'issue': issue
        })

    print(f"\nWill update {len(corrections)} movies")
    if len(skipped) > 0:
        print(f"Skipped {len(skipped)} movies (no common words):")
        for s in skipped[:5]:  # Show first 5
            print(f"  {s['movieId']}: '{s['movielens_title']}' vs '{s['api_title']}'")

    if len(corrections) == 0:
        print("No corrections to apply")
        return

    # Convert to DataFrame
    corrections_df = pl.DataFrame(corrections)

    # Join with movies and update titles
    updated_movies = movies_df.join(
        corrections_df.select(["movieId", "corrected_title"]),
        on="movieId",
        how="left"
    ).with_columns([
        # Use corrected title if available, otherwise keep original
        pl.coalesce([pl.col("corrected_title"), pl.col("title")]).alias("title")
    ]).select(movies_df.columns)  # Keep original column order

    # Write updated movies back
    updated_movies.write_csv(movies_path)

    # Remove fixed rows from imdb_mismatches.csv using anti-join
    updated_mismatches = mismatches_df.join(
        corrections_df.select(["movieId"]),
        on="movieId",
        how="anti"
    )

    # Write updated mismatches back
    updated_mismatches.write_csv(mismatches_path)

    print(f"\n{'='*60}")
    print(f"Updated {movies_path} with {len(corrections)} corrected titles")
    print(f"Updated {mismatches_path} - removed {len(corrections)} fixed rows")
    print(f"Remaining mismatches: {len(updated_mismatches)}")
    print(f"\nSample corrections:")

    # Show some examples
    examples = corrections_df.head(10)
    for row in examples.iter_rows(named=True):
        print(f"  [{row['issue']}] {row['movieId']}: '{row['original_title']}' → '{row['corrected_title']}'")
