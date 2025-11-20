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
        movie_year_output_path = os.path.join(current_dir, "..", "..", "datasets", "output", "movie_year.npy")
        overview_dir_cast_emb_path = os.path.join(current_dir, "..", "..", "datasets", "output", "overview_dir_cast_embeddings.npy")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output", "movie-metadata.csv")
        api_genre_mlb_path = os.path.join(current_dir, "..", "..", "..", "api", "app", "model", "files", "genre_mlb.joblib")
        training_genre_mlb_path = os.path.join(current_dir, "..", "..", "datasets", "output", "genre_mlb.joblib")
    else:
        movie_title_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "title_embeddings.npy")
        movie_genre_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "genre_mlb.npy")
        movie_year_output_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "movie_year.npy")
        overview_dir_cast_emb_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "overview_dir_cast_embeddings.npy")
        movie_metadata_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "movie-metadata.csv")
        api_genre_mlb_path = os.path.join(current_dir, "..", "..", "..", "api", "app", "model", "files_small", "genre_mlb.joblib")
        training_genre_mlb_path = os.path.join(current_dir, "..", "..", "datasets", "output-small", "genre_mlb.joblib")
    
    model = SentenceTransformer('intfloat/multilingual-e5-small')
    mlb = MultiLabelBinarizer()
    metadata_df = pl.read_csv(movie_metadata_path)


    titles = metadata_df.get_column('title')
    genres = metadata_df.get_column('genres_normalized').str.split('|')
    years = metadata_df.get_column('year')

    title_embeddings = model.encode(titles, convert_to_numpy=True) # 384-dim

    np.save(movie_title_output_path, title_embeddings) 

    genre_mlb = mlb.fit_transform(genres) # create genre matrix, shape = [num_movies, num_genres]
    
    np.save(movie_genre_output_path, genre_mlb)

    year_normalized = ((years - 1900) / 125.0).to_numpy() # Normalizes it to a value between [0, 1]
    np.save(movie_year_output_path, year_normalized)

    # created a sentence containing overview, directors and top 15 actors to be used to create 
    # sentence embeddings 
    movie_overview_director_actor_text = (
        metadata_df
        .select([
            pl.when(pl.col('overview').is_not_null())
                .then(pl.col('overview'))
                .otherwise(pl.lit(''))
                .alias('overview_text'),
            pl.when(pl.col('director').is_not_null())
                .then(pl.concat_str([pl.lit('Directed by '), pl.col('director').str.replace('|', ', ')]))
                .otherwise(pl.lit(''))
                .alias('director_text'),
            pl.when(pl.col('cast_normalized').is_not_null())
                .then(
                    pl.concat_str([
                        pl.lit('Starring '),
                        pl.col('cast_normalized').str.split('|').list.head(15).list.join(', ')
                    ])
                )
                .otherwise(pl.lit(''))
                .alias('cast_text')
        ])
        .select(
            pl.concat_str(
                [pl.col('overview_text'), pl.col('director_text'), pl.col('cast_text')],
                separator='. '
            ).str.strip_chars('. ')
        )
        .to_series()
        .to_list()
    )

    # 384-dim
    movie_overview_dir_actor_embeddings = model.encode(movie_overview_director_actor_text, convert_to_numpy=True)
    np.save(overview_dir_cast_emb_path, movie_overview_dir_actor_embeddings)

    # Save the MLB object itself for api (to transform new user and movie genres)
    # and also to be used for training
    joblib.dump(mlb, api_genre_mlb_path)
    joblib.dump(mlb, training_genre_mlb_path)