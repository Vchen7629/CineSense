from csv_cleaning_utils.removie_invalid_characters import remove_invalid_character
from csv_cleaning_utils.remove_invalid_movies import remove_invalid_movies
from csv_cleaning_utils.update_tmdb_id import update_tmdb_id
from csv_cleaning_utils.fix_mismatches import fix_movie_mismatches
from csv_cleaning_utils.remove_duplicate_tmdbIds import remove_duplicate_tmdb_ids
import os

def run_clean_csv_functions(init: bool = True, large_dataset: bool = False):
    current_dir = os.path.dirname(__file__)

    if large_dataset:
        movies_path = os.path.join(current_dir, "..", "datasets", "ml-latest", "movies.csv")
        links_path = os.path.join(current_dir, "..", "datasets", "ml-latest", "links.csv")
        imdb_mismatches_path = os.path.join(current_dir, "..", "datasets", "cleaning-files", "imdb_mismatches.csv")
        duplicate_id_path = os.path.join(current_dir, "..", "datasets", "cleaning-files", "duplicate_id.csv")
        ratings_path = os.path.join(current_dir, "..", "datasets", "ml-latest", "ratings.csv")
    else:
        movies_path = os.path.join(current_dir, "..", "datasets", "ml-latest-small", "movies.csv")
        links_path = os.path.join(current_dir, "..", "datasets", "ml-latest-small", "links.csv")
        imdb_mismatches_path = os.path.join(current_dir, "..", "datasets", "cleaning-files-small", "imdb_mismatches.csv")
        duplicate_id_path = os.path.join(current_dir, "..", "datasets", "cleaning-files-small", "duplicate_id.csv")
        ratings_path = os.path.join(current_dir, "..", "datasets", "ml-latest-small", "ratings.csv")

    if init: # clean the original dataset by removing incorrect characters
        remove_invalid_character()

    # Check all movies via IMDB ID lookup
    # - Updates links.csv with correct TMDB IDs where title and year match
    # - Writes all mismatches (TV shows, 404s, title/year mismatches) to imdb_mismatches.csv
    #update_tmdb_id(movies_path, links_path, imdb_mismatches_path)

    # Find duplicate movies with the same tmdbid
    # - db depnds on tmdbId as primary key so this is to prevent duplicate key errors
    # - saves the duplicates to a csv for manual review
    remove_duplicate_tmdb_ids(links_path, movies_path, ratings_path, duplicate_id_path)

    # Fix title and year mismatches in movies.csv
    # - Only fixes if titles share common words
    #fix_movie_mismatches(movies_path, imdb_mismatches_path)

    # Remove TV shows and 404s from the dataset
    # - All other issues are kept for manual review
    #remove_invalid_movies(movies_path, links_path, imdb_mismatches_path, large_dataset)

if __name__ == "__main__":
    run_clean_csv_functions(init=False)
