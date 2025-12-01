
def upsert_movie_rating_stats(cursor, rating_stats_df):
      print(f"Upserting {len(rating_stats_df)} rating stats into movie_rating_stats...")

      for row in rating_stats_df.iter_rows(named=True):
          cursor.execute("""
              INSERT INTO movie_rating_stats (
                  movie_id, tmdb_avg_rating, tmdb_vote_log, tmdb_popularity
              )
              VALUES (%s, %s, %s, %s)
              ON CONFLICT (movie_id) DO UPDATE SET
                  tmdb_avg_rating = EXCLUDED.tmdb_avg_rating,
                  tmdb_vote_log = EXCLUDED.tmdb_vote_log,
                  tmdb_popularity = EXCLUDED.tmdb_popularity,
                  last_updated = NOW()
          """, (
              str(row['movie_id']),
              float(row['vote_average']),
              float(row['vote_count']),
              float(row['popularity'])
          ))

      print("Movie rating stats upserted")