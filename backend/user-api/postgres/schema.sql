-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users login table
CREATE TABLE IF NOT EXISTS user_login (
    user_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Movie metadata table
CREATE TABLE IF NOT EXISTS movie_metadata (
    movie_id TEXT PRIMARY KEY,
    movie_name TEXT NOT NULL,
    genre TEXT NOT NULL,
    release_date TEXT NOT NULL,
    summary TEXT NOT NULL
);

-- User ratings table
CREATE TABLE IF NOT EXISTS user_ratings (
    rating_id SERIAL PRIMARY KEY,
    user_id SERIAL NOT NULL,
    movie_id TEXT NOT NULL,
    user_rating INT NOT NULL,
    added_at TIMESTAMP NOT NULL,

    FOREIGN KEY (user_id) REFERENCES user_login(user_id),
    FOREIGN KEY (movie_id) REFERENCES movie_metadata(movie_id)
);

-- User watchlist table
CREATE TABLE IF NOT EXISTS user_watchlist (
    movie_id TEXT PRIMARY KEY,
    user_id SERIAL NOT NULL,
    added_at TIMESTAMP NOT NULL,

    FOREIGN KEY (user_id) REFERENCES user_login(user_id),
    FOREIGN KEY (movie_id) REFERENCES movie_metadata(movie_id)
);


-- Movie vectors table
CREATE TABLE IF NOT EXISTS movie_vectors (
    id SERIAL PRIMARY KEY,
    movie_id TEXT UNIQUE NOT NULL,
    embedding VECTOR(128)
);

-- User vectors table
CREATE TABLE IF NOT EXISTS user_vectors (
    id SERIAL PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    embedding VECTOR(128)
);
