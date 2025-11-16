import polars as pl

# load user top-3 genres and movie genres
def load_genre_mappings(user_genres_path: str, movie_metadata_path: str):
    user_genres_df = pl.read_csv(user_genres_path)
    movies_metadata_df = pl.read_csv(movie_metadata_path)

    user_to_genres = {
        row['userId']: set(row['genres'].split('|'))
        for row in user_genres_df.iter_rows(named=True)
    }
    
    movies_to_genres = {}
    for row in movies_metadata_df.select(['movie_idx', 'genres_normalized']).iter_rows(named=True):
        genres = set(row['genres_normalized'].split('|'))
        movies_to_genres[row['movie_idx']] = genres

    return user_to_genres, movies_to_genres
