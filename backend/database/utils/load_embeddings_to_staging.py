
# Load embeddings into staging table
def load_embeddings_to_staging(cursor, metadata_df, embeddings, staging_table):
    print(f"Loading {len(embeddings)} embeddings into {staging_table}...")

    # Validate data consistency
    if len(metadata_df) != len(embeddings):
        raise ValueError(
            f"Data mismatch: {len(metadata_df)} movies in metadata "
            f"but {len(embeddings)} embeddings"
        )

    # Truncate staging table
    cursor.execute(f"TRUNCATE TABLE {staging_table}")
    print(f"✓ Truncated {staging_table}")

    # Insert embeddings
    for idx, row in enumerate(metadata_df.iter_rows(named=True)):
        embedding_list = embeddings[idx].tolist()

        cursor.execute(f"""
            INSERT INTO {staging_table} (movie_id, embedding)
            VALUES (%s, %s::vector)
        """, (
            str(row['tmdbId']),
            embedding_list
        ))

    print(f"Loaded embeddings into {staging_table}")