import os
from preprocessing.candidate_generation_utils.filter_positive_ratings import filter_positive_ratings
from preprocessing.candidate_generation_utils.add_movie_idx import add_movie_user_idx_mapping
from preprocessing.candidate_generation_utils.movie_metadata import create_movies_metadata
from preprocessing.candidate_generation_utils.movie_embedding import create_movie_embeddings
from preprocessing.candidate_generation_utils.user_cold_start_embedding import create_user_preferred_genres_embedding
from preprocessing.candidate_generation_utils.cold_start_negative_sampling import cold_start_negative_sampling
from preprocessing.candidate_generation_utils.collaborative_filtering_neg_sampling import collaborative_filtering_negative_sampling
# preprocessing functions for the candidate generation two tower model

current_dir = os.path.dirname(__file__)

def preprocess_candidate_generation_model_files(cold_start: bool = True):

    # create a user-output.csv containing only the positive rated movies
    filter_positive_ratings(large_dataset=False)

    # creates a movie-output.csv and adds a movie_idx mapping to user-output.csv
    add_movie_user_idx_mapping(large_dataset=False)

    # creates the movie-metadata.csv that contains the movie and all its metadata
    create_movies_metadata(large_dataset=False)

    # create embedding files for movie title and genre and exports the genre mlb for use later
    create_movie_embeddings(large_dataset=False)

    if cold_start:
        # create the embedding file containing user's top 3 genres as preferred-genres.npy to be used for training
        create_user_preferred_genres_embedding(large_dataset=False)
        cold_start_negative_sampling(large_dataset=False)
    else:
        collaborative_filtering_negative_sampling(large_dataset=False)

if __name__ == "__main__":
    preprocess_candidate_generation_model_files(cold_start=False)