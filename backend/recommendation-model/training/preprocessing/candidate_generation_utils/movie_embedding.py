import os
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MultiLabelBinarizer
import polars as pl
import numpy as np
import joblib

current_dir = os.path.dirname(__file__)

# creates numpy files containing the embeddings:
#   - Movie title: Embedded using a bert model
#   - Movie genres: Embedded using mlb
def create_movie_embeddings(large_dataset: bool = False) -> None:
    if large_dataset:
        movie_title_output_path = os.path.join(current_dir, "..", "..", "datasets", "output", "title_embeddings.npy")
        movie_genre_output_path = os.path.join(current_dir, "..", "..", "datasets", "output", "genre_mlb.npy")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output", "movie-metadata.csv")
        api_genre_mlb_path = os.path.join(current_dir, "..", "..", "..", "api", "app", "model", "files", "genre_mlb.joblib")
        training_genre_mlb_path = os.path.join(current_dir, "..", "..", "datasets", "output", "genre_mlb.joblib")
    else:
        movie_title_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "title_embeddings.npy")
        movie_genre_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "genre_mlb.npy")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "movie-metadata.csv")
        api_genre_mlb_path = os.path.join(current_dir, "..", "..", "..", "api", "app", "model", "files_small", "genre_mlb.joblib")
        training_genre_mlb_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "genre_mlb.joblib")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    mlb = MultiLabelBinarizer()
    metadata_df = pl.read_csv(movie_metadata_path)


    titles = metadata_df.get_column('title')
    genres = metadata_df.get_column('genres_normalized').str.split('|')

    title_embeddings = model.encode(titles, convert_to_numpy=True) # 384-dim

    np.save(movie_title_output_path, title_embeddings) 

    genre_mlb = mlb.fit_transform(genres) # create genre matrix, shape = [num_movies, num_genres]
    
    np.save(movie_genre_output_path, genre_mlb)

    # Save the MLB object itself for api (to transform new user and movie genres)
    # and also to be used for training
    joblib.dump(mlb, api_genre_mlb_path)
    joblib.dump(mlb, training_genre_mlb_path)