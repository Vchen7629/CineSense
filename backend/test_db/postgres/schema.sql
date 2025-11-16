-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users login table
CREATE TABLE IF NOT EXISTS user_login (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Movie metadata table
CREATE TABLE IF NOT EXISTS movie_metadata (
    movie_id TEXT PRIMARY KEY,
    movie_name TEXT NOT NULL,
    genres TEXT[] NOT NULL,
    release_date INTEGER NOT NULL,
    summary TEXT NOT NULL,
    actors TEXT[] NOT NULL,
    director TEXT[] NOT NULL,
    poster_path TEXT
);

-- User watchlist table
CREATE TABLE IF NOT EXISTS user_watchlist (
    user_id TEXT NOT NULL,
    movie_id TEXT NOT NULL,
    user_rating INT,
    added_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    PRIMARY KEY (user_id, movie_id),
    FOREIGN KEY (user_id)
        REFERENCES user_login(user_id)
        ON DELETE CASCADE,
    FOREIGN KEY (movie_id)
        REFERENCES movie_metadata(movie_id)
        ON DELETE CASCADE
);

-- Movie embedding tables
CREATE TABLE IF NOT EXISTS movie_embedding_coldstart (
    movie_id TEXT PRIMARY KEY,
    embedding VECTOR(512) NOT NULL,

    FOREIGN KEY (movie_id)
        REFERENCES movie_metadata(movie_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS movie_embedding_personalized (
    movie_id TEXT PRIMARY KEY,
    embedding VECTOR(512) NOT NULL,

    FOREIGN KEY (movie_id)
        REFERENCES movie_metadata(movie_id)
        ON DELETE CASCADE
);

--- User Embedding Tables
CREATE TABLE IF NOT EXISTS user_embeddings (
    user_id TEXT PRIMARY KEY,
    embedding VECTOR(512) NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id)
        REFERENCES user_login(user_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_genre_embeddings (
    user_id TEXT PRIMARY KEY,
    genre_embedding VECTOR(512) NOT NULL,
    top_3_genres TEXT[] NOT NULL,
    last_updated TIMESTAMP DEFAULT NOW(),

    FOREIGN KEY (user_id)
        REFERENCES user_login(user_id)
        ON DELETE CASCADE
);

--- Indexes
CREATE INDEX ON movie_metadata USING GIN (genres);
CREATE INDEX ON movie_embedding_coldstart USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON movie_embedding_personalized USING hnsw (embedding vector_cosine_ops);
CREATE INDEX ON user_embeddings USING hnsw (embedding vector_cosine_ops);
