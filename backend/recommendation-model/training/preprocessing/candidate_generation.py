import polars as pl
from .candidate_generation_utils.filter_positive_ratings import filter_positive_ratings
from .candidate_generation_utils.add_movie_idx import add_movie_user_idx_mapping
from .candidate_generation_utils.movie_metadata import create_movies_metadata
from .candidate_generation_utils.movie_embedding import create_movie_embeddings
from .candidate_generation_utils.user_cold_start_embedding import create_user_preferred_genres_embedding
from .candidate_generation_utils.cold_start_negative_sampling import cold_start_negative_sampling
from .candidate_generation_utils.collaborative_filtering_neg_sampling import collaborative_filtering_negative_sampling
from .candidate_generation_utils.fetch_missing_movies import run_fetch_movies
from shared.path_config import path_helper

# preprocessing functions for the candidate generation two tower model
def preprocess_candidate_generation_model_files(cold_start: bool = True, large_dataset: bool = False):
    paths = path_helper(large_dataset=large_dataset)

    missing_metadata_path = paths.missing_movie_metadata_path
    positive_ratings_path = paths.pos_ratings_path
    negative_ratings_path = paths.neg_ratings_path
    movielens_links_path = paths.movielens_links_path
    
    # create a user-output.csv containing only the positive rated movies
    filter_positive_ratings(positive_ratings_path, negative_ratings_path, movielens_links_path, large_dataset)

    # creates a movie-output.csv and adds a movie_idx mapping to user-output.csv
    add_movie_user_idx_mapping(positive_ratings_path, negative_ratings_path, large_dataset)

    # creates the movie-metadata.csv that contains the movie and all its metadata
    create_movies_metadata(missing_metadata_path, movielens_links_path, large_dataset)

    # check if there are any rows with missing metadata
    missing_metadata_df = pl.read_csv(missing_metadata_path)
    if not missing_metadata_df.is_empty():
        print(f"Found {len(missing_metadata_df)} movies with missing metadata. Fetching from API...")
        run_fetch_movies(large_dataset=large_dataset) # fetching movie metadata with tmdb and omdb api and writing it to the metadata csv
        create_movies_metadata(missing_metadata_path, movielens_links_path, large_dataset) # rerun to update the metadata csv with the fetched metadata
    else:
        print("No missing metadata found. Skipping API fetch.")

    # create embedding files for movie title and genre and exports the genre mlb for use later
    #create_movie_embeddings(large_dataset=large_dataset)

    if cold_start:
        # create the embedding file containing user's top 3 genres as preferred-genres.npy to be used for training
        create_user_preferred_genres_embedding(positive_ratings_path, large_dataset=large_dataset)
        cold_start_negative_sampling(
            positive_ratings_path=positive_ratings_path,
            negative_ratings_path=negative_ratings_path, 
            large_dataset=large_dataset
        )
    else:
        collaborative_filtering_negative_sampling(
            positive_ratings_path=positive_ratings_path,
            negative_ratings_path=negative_ratings_path, 
            large_dataset=large_dataset
        )

if __name__ == "__main__":
    preprocess_candidate_generation_model_files(cold_start=True)