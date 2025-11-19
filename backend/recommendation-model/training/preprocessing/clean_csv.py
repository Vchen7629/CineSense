from csv_cleaning_utils.invalid_chars import clean_csv
from csv_cleaning_utils.check_tmdb_id import check_tmdb_ids
from csv_cleaning_utils.remove_invalid_movies import remove_invalid_movies
from csv_cleaning_utils.find_duplicate_tmdb_ids import find_duplicate_tmdb_ids
import os

def run_clean_csv_functions(init: bool = True, large_dataset: bool = False):
    current_dir = os.path.dirname(__file__)

    if large_dataset:
        movies_path = os.path.join(current_dir, "..", "datasets", "ml-latest", "movies.csv")
        links_path = os.path.join(current_dir, "..", "datasets", "ml-latest", "links.csv")
        tmdb_mismatched_path = os.path.join(current_dir, "..", "datasets", "output", "tmdb_mismatches.csv")
        duplicate_ids_path = os.path.join(current_dir, "..", "datasets", "output", "duplicate_ids.csv")
    else:
        movies_path = os.path.join(current_dir, "..", "datasets", "ml-latest-small", "movies.csv")
        links_path = os.path.join(current_dir, "..", "datasets", "ml-latest-small", "links.csv")
        tmdb_mismatched_path = os.path.join(current_dir, "..", "datasets", "output-small", "tmdb_mismatches.csv")
        duplicate_ids_path = os.path.join(current_dir, "..", "datasets", "output-small", "duplicate_ids.csv")


    if init: # clean the original dataset by removing incorrect characters
        clean_csv()

    # check duplicates and filter out tvshows to write to a csv to be used later
    #find_duplicate_tmdb_ids(links_path, movies_path, duplicate_ids_path)

    remove_invalid_movies(movies_path, links_path, duplicate_ids_path, large_dataset)


    # check the links.py tmdbid using the api to see if theyre valid movies that match what the 
    # api returns (uses title and year), 
    #check_tmdb_ids(movies_path, links_path, tmdb_mismatched_path)

    #remove_invalid_movies(movies_path, links_path, tmdb_mismatched_path, large_dataset)

if __name__ == "__main__":
    run_clean_csv_functions(init=False)

