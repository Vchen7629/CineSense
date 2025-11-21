import os
from reranker_utils.user_rated_count import user_rated_movie_count
from reranker_utils.user_num_liked_feature import user_num_liked_feature
from reranker_utils.movie_rating_count import movie_rating_count
from reranker_utils.avg_rating import avg_rating
from reranker_utils.movie_year_features import movie_year_features
from reranker_utils.movie_language_feature import movie_language_feature
from reranker_utils.movie_tmdb_features import movie_tmdb_features
from reranker_utils.movie_genre_features import movie_genre_features
from reranker_utils.movie_cast_director_count import movie_cast_director_count
from reranker_utils.generate_favorite_cast_director import generate_favorite_cast_director

# preprocessing functions for generating the csv dataset for lightgbm reranking model

current_dir = os.path.dirname(__file__)

def preprocess_reranking_model_files(large_dataset: bool = False):
    if large_dataset:
        reranker_user_features_path = os.path.join(current_dir, "..", "datasets", "output", "reranker-user-features.csv")
        reranker_movie_features_path = os.path.join(current_dir, "..", "datasets", "output", "reranker-movie-features.csv")
        pos_ratings_path = os.path.join(current_dir, "..", "datasets", "output", "user-positive-ratings.csv")
        neg_ratings_path = os.path.join(current_dir, "..", "datasets", "output", "user-negative-ratings.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "datasets", "output", "movie-metadata.csv")
    else:
        reranker_user_features_path = os.path.join(current_dir, "..", "datasets", "output-small", "reranker-user-features.csv")
        reranker_movie_features_path = os.path.join(current_dir, "..", "datasets", "output-small", "reranker-movie-features.csv")
        pos_ratings_path = os.path.join(current_dir, "..", "datasets", "output-small", "user-positive-ratings.csv")
        neg_ratings_path = os.path.join(current_dir, "..", "datasets", "output-small", "user-negative-ratings.csv")
        movie_metadata_path = os.path.join(current_dir, "..", "datasets", "output-small", "movie-metadata.csv")

    user_rated_movie_count(reranker_user_features_path, pos_ratings_path, neg_ratings_path)
    # calculate the average rating the user gives to their rated movies
    avg_rating(
        feature_id="userId",
        column_name="user_rating_count",
        new_col_name="user_avg_rating",
        reranker_features_path=reranker_user_features_path, 
        pos_ratings_path=pos_ratings_path, 
        neg_ratings_path=neg_ratings_path
    )

    # create columnS containing the num of liked actors/directors/genres based on their pos rated movies
    user_num_liked_feature("genres_normalized", "num_user_genres", reranker_user_features_path, movie_metadata_path, pos_ratings_path)
    user_num_liked_feature("cast_normalized", "num_user_actors", reranker_user_features_path, movie_metadata_path, pos_ratings_path)
    user_num_liked_feature("director", "num_user_director", reranker_user_features_path, movie_metadata_path, pos_ratings_path)


    movie_rating_count(reranker_movie_features_path, pos_ratings_path, neg_ratings_path)

    # calculate the average rating given to the movie from every user who rated it
    avg_rating(
        feature_id="movie_idx",
        column_name="movie_rating_count",
        new_col_name="movie_avg_rating",
        reranker_features_path=reranker_movie_features_path, 
        pos_ratings_path=pos_ratings_path, 
        neg_ratings_path=neg_ratings_path
    )

    # create movie year related features such as year, age, and recency score
    movie_year_features(reranker_movie_features_path, movie_metadata_path)

    movie_language_feature(reranker_movie_features_path, movie_metadata_path)

    # add tmdb features for each movie
    movie_tmdb_features(reranker_movie_features_path, movie_metadata_path)

    # add movie genre related features
    movie_genre_features(reranker_movie_features_path, movie_metadata_path)

    # add movie cast related features
    movie_cast_director_count(reranker_movie_features_path, movie_metadata_path)

    # generate a string containing top 50 actors and top 10 director for each user using their positive rated movies
    generate_favorite_cast_director(movie_metadata_path, pos_ratings_path, large_dataset)

    # add a count for how much directors and cast members in each movie
    movie_cast_director_count(reranker_movie_features_path, movie_metadata_path)

if __name__ == "__main__":
    preprocess_reranking_model_files(large_dataset=False)