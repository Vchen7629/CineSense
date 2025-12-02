
def upsert_movie_metadata(cursor, metadata_df):
    print(f"Upserting {len(metadata_df)} movies into movie_metadata...")

    for row in metadata_df.iter_rows(named=True):
        cursor.execute("""
            INSERT INTO movie_metadata (
                movie_id, movie_name, genres, release_date, summary, actors, director, language, poster_path
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (movie_id) DO UPDATE SET
                movie_name = EXCLUDED.movie_name,
                genres = EXCLUDED.genres,
                release_date = EXCLUDED.release_date,
                summary = EXCLUDED.summary,
                actors = EXCLUDED.actors,
                director = EXCLUDED.director,
                language = EXCLUDED.language,
                poster_path = EXCLUDED.poster_path
        """, (
            str(row['tmdbId']),
            row['title'],
            row['genres_normalized'].split("|") if isinstance(row['genres_normalized'], str) else row['genres_normalized'],
            int(row['year']),
            row['overview'],
            row['cast_normalized'].split("|") if isinstance(row['cast_normalized'], str) else row['cast_normalized'],
            row['director'].split("|") if isinstance(row['director'], str) else row['director'],
            row.get('original_language'),
            row.get('poster_path', '')
        ))

    print("Movie metadata upserted")