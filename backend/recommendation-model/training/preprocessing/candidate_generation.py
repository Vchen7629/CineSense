import os
import polars as pl
from preprocessing.candidate_generation_utils.filter_positive_ratings import filter_positive_ratings
from preprocessing.candidate_generation_utils.add_movie_idx import add_movie_user_idx_mapping
from preprocessing.candidate_generation_utils.movie_metadata import create_movies_metadata
from preprocessing.candidate_generation_utils.movie_embedding import create_movie_embeddings
from preprocessing.candidate_generation_utils.user_cold_start_embedding import create_user_preferred_genres_embedding
from preprocessing.candidate_generation_utils.cold_start_negative_sampling import cold_start_negative_sampling
from preprocessing.candidate_generation_utils.collaborative_filtering_neg_sampling import collaborative_filtering_negative_sampling
from preprocessing.candidate_generation_utils.fetch_missing_movies import run_fetch_movies

# preprocessing functions for the candidate generation two tower model

current_dir = os.path.dirname(__file__)

def preprocess_candidate_generation_model_files(cold_start: bool = True, large_dataset: bool = False):
    if large_dataset:
        missing_metadata_path = os.path.join(current_dir, "..", "datasets", "output", "missing-metadata.csv")
    else:
        missing_metadata_path = os.path.join(current_dir, "..", "datasets", "output-small", "missing-metadata.csv")

    # create a user-output.csv containing only the positive rated movies
    filter_positive_ratings(large_dataset=large_dataset)

    # creates a movie-output.csv and adds a movie_idx mapping to user-output.csv
    add_movie_user_idx_mapping(large_dataset=large_dataset)

    # creates the movie-metadata.csv that contains the movie and all its metadata
    create_movies_metadata(large_dataset=large_dataset)

    # check if there are any rows with missing metadata
    missing_metadata_df = pl.read_csv(missing_metadata_path)
    if not missing_metadata_df.is_empty():
        print(f"Found {len(missing_metadata_df)} movies with missing metadata. Fetching from API...")
        run_fetch_movies(large_dataset=large_dataset) # fetching movie metadata with tmdb and omdb api and writing it to the metadata csv
        create_movies_metadata(large_dataset=large_dataset) # rerun to update the metadata csv with the fetched metadata
    else:
        print("No missing metadata found. Skipping API fetch.")

    # create embedding files for movie title and genre and exports the genre mlb for use later
    #create_movie_embeddings(large_dataset=large_dataset)

    if cold_start:
        # create the embedding file containing user's top 3 genres as preferred-genres.npy to be used for training
        create_user_preferred_genres_embedding(large_dataset=large_dataset)
        cold_start_negative_sampling(large_dataset=large_dataset)
    else:
        collaborative_filtering_negative_sampling(large_dataset=large_dataset)

if __name__ == "__main__":
    preprocess_candidate_generation_model_files(cold_start=True)