from sqlalchemy import Column, String, Integer, REAL, TIMESTAMP, ForeignKey, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
from pgvector.sqlalchemy import Vector

Base = declarative_base()

# Declaring sqlalchemy Postgres table schemas
class UserLogin(Base):
    __tablename__ = 'user_login'

    user_id = Column(Text, primary_key=True)
    username = Column(Text, nullable=False)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default='NOW()')

class Session(Base):
    __tablename__ = "sessions"

    user_id = Column(Text, ForeignKey("user_login.user_id", ondelete="CASCADE"), primary_key=True, unique=True, index=True)
    session_token = Column(Text, index=True, nullable=False)
    created_at = Column(DateTime(timezone = True), server_default='NOW()')
    expire_at = Column(DateTime(timezone=True), nullable=False)

class MovieMetadata(Base):
    __tablename__ = 'movie_metadata'
    
    movie_id = Column(Text, primary_key=True)
    movie_name = Column(Text, nullable=False)
    genres = Column(PG_ARRAY(Text), nullable=False)
    release_date = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    actors = Column(PG_ARRAY(Text), nullable=False)
    director = Column(PG_ARRAY(Text), nullable=False)
    poster_path = Column(Text, server_default='')
    
    __table_args__ = (
        Index('idx_movie_metadata_genres', 'genres', postgresql_using='gin'),
    )

class UserWatchlist(Base):
    __tablename__ = 'user_watchlist'
    
    user_id = Column(Text, ForeignKey('user_login.user_id', ondelete='CASCADE'), primary_key=True)
    movie_id = Column(Text, ForeignKey('movie_metadata.movie_id', ondelete='CASCADE'), primary_key=True)
    user_rating = Column(REAL, server_default='0.0')
    added_at = Column(TIMESTAMP, server_default='NOW()')
    updated_at = Column(TIMESTAMP, server_default='NOW()')

class MovieRatingStats(Base):
    __tablename__ = 'movie_rating_stats'
    
    movie_id = Column(Text, ForeignKey('movie_metadata.movie_id', ondelete='CASCADE'), primary_key=True)
    avg_rating = Column(REAL, server_default='0.0')
    rating_count = Column(Integer, server_default='0')
    rating_count_log = Column(REAL, server_default='0.0')
    tmdb_avg_rating = Column(REAL, server_default='0.0')
    tmdb_vote_log = Column(REAL, server_default='0.0')
    tmdb_popularity = Column(REAL, server_default='0.0')
    last_updated = Column(TIMESTAMP, server_default='NOW()')

class UserRatingStats(Base):
    __tablename__ = 'user_rating_stats'
    
    user_id = Column(Text, ForeignKey('user_login.user_id', ondelete='CASCADE'), primary_key=True)
    avg_rating = Column(REAL, server_default='0.0')
    rating_count = Column(Integer, server_default='0')
    rating_count_log = Column(REAL, server_default='0.0')
    top_3_genres = Column(PG_ARRAY(Text), server_default='{}')
    top_50_actors = Column(PG_ARRAY(Text), server_default='{}')
    top_10_directors = Column(PG_ARRAY(Text), server_default='{}')
    last_updated = Column(TIMESTAMP, server_default='NOW()')

class MovieEmbeddingColdstart(Base):
    __tablename__ = 'movie_embedding_coldstart'
    
    movie_id = Column(Text, ForeignKey('movie_metadata.movie_id', ondelete='CASCADE'), primary_key=True)
    embedding = Column(Vector(512), nullable=False)
    
    __table_args__ = (
        Index('idx_movie_embedding_coldstart_hnsw', 'embedding', 
              postgresql_using='hnsw',
              postgresql_with={'m': 16, 'ef_construction': 64},
              postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )

class MovieEmbeddingPersonalized(Base):
    __tablename__ = 'movie_embedding_personalized'
    
    movie_id = Column(Text, ForeignKey('movie_metadata.movie_id', ondelete='CASCADE'), primary_key=True)
    embedding = Column(Vector(512), nullable=False)
    
    __table_args__ = (
        Index('idx_movie_embedding_personalized_hnsw', 'embedding',
              postgresql_using='hnsw',
              postgresql_with={'m': 16, 'ef_construction': 64},
              postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )

class UserEmbeddings(Base):
    __tablename__ = 'user_embeddings'
    
    user_id = Column(Text, ForeignKey('user_login.user_id', ondelete='CASCADE'), primary_key=True)
    embedding = Column(Vector(512), nullable=False)
    last_updated = Column(TIMESTAMP, server_default='NOW()')
    
    __table_args__ = (
        Index('idx_user_embeddings_hnsw', 'embedding',
              postgresql_using='hnsw',
              postgresql_with={'m': 16, 'ef_construction': 64},
              postgresql_ops={'embedding': 'vector_cosine_ops'}),
    )

class UserGenreEmbeddings(Base):
    __tablename__ = 'user_genre_embeddings'
    
    user_id = Column(Text, ForeignKey('user_login.user_id', ondelete='CASCADE'), primary_key=True)
    genre_embedding = Column(Vector(512), nullable=False)
    last_updated = Column(TIMESTAMP, server_default='NOW()')