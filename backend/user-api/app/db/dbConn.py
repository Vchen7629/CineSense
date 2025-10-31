# Code for connecting to the PostgreSQL Database
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg://postgres:password@localhost:5432/example_db")
