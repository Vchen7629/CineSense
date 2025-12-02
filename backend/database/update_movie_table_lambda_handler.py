import json
import boto3
import psycopg2
import numpy as np
import polars as pl
from io import BytesIO
from utils.upsert_movie_metadata_table import upsert_movie_metadata
from utils.upsert_movie_rating_stats import upsert_movie_rating_stats
from utils.load_embeddings_to_staging import load_embeddings_to_staging
from utils.swap_tables import swap_tables
from utils.get_aws_rds_credentials import get_db_credentials

# Download file from S3 to memory
def download_from_s3(s3_client, bucket, key):
    try:
        buffer = BytesIO()
        s3_client.download_fileobj(bucket, key, buffer)
        buffer.seek(0)
        print(f"Downloaded s3://{bucket}/{key}")
        return buffer
    except Exception as e:
        raise Exception(f"failed to download s3://{bucket}/{key}: {e}")
    
# Load CSV from S3 into Polars Dataframe
def load_csv_from_s3(s3_client, bucket, key):
    buffer = download_from_s3(s3_client, bucket, key)
    df = pl.read_csv(buffer)
    return df

def load_npy_from_s3(s3_client, bucket, key):
    buffer = download_from_s3(s3_client, bucket, key)
    embeddings = np.load(buffer)
    return embeddings

def parse_s3_event(event):
    s3_record = event['Records'][0]['s3']
    bucket = s3_record['bucket']['name']
    key = s3_record['object']['key']

    # parse key to determine file type and version
    parts = key.split('/')

    if key.startswith('movie_metadata/'):
        file_type = 'metadata'
        version = parts[2]
        model_type = None
    elif key.startswith('movie_ratings/'):
        file_type = 'ratings'
        version = parts[2]
        model_type = None
    elif key.startswith('movie_embeddings/cold_start/'):
        file_type = 'embeddings'
        model_type = 'cold_start'
        version = parts[3]
    elif key.startswith('movie_embeddings/collaborative/'):
        file_type = 'embeddings'
        model_type = 'collaborative'
        version = parts[3]
    else:
        raise ValueError(f"Unknown S3 key pattern: {key}")

    return {
        'bucket': bucket,
        'key': key,
        'file_type': file_type,
        'model_type': model_type,
        'version': version
    }

# Lambda handle that runs Alembic migrations
def handler(event, context):
    try:
        event_info = parse_s3_event(event)
        bucket = event_info['bucket']
        key = event_info['key']
        file_type = event_info['file_type']
        model_type = event_info['model_type']
        version = event_info['version']

        # Fetch DB credentials from Secrets Manager
        db_creds = get_db_credentials()
        s3_client = boto3.client('s3')

        conn = psycopg2.connect(
            host=db_creds['host'],
            port=db_creds['port'],
            dbname=db_creds['dbname'],
            user=db_creds['username'],
            password=db_creds['password']
        )
        cursor = conn.cursor()
        print("Connected to database")

        print(f"DEBUG: file_type={file_type}, bucket={bucket}, key={key}")

        # Process based on file type
        if file_type == 'metadata':
            print("Downloading metadata CSV from S3...")
            metadata_df = load_csv_from_s3(s3_client, bucket, key)
            print("Downloaded metadata CSV from S3!")
            print("Updating movie metadata...")
            upsert_movie_metadata(cursor, metadata_df)
            print("Updated movie metadata!")

        elif file_type == 'ratings':
            print("Downloading ratings CSV from S3...")
            rating_stats_df = load_csv_from_s3(s3_client, bucket, key)
            print("Downloaded ratings CSV from S3!")
            print("Updating movie ratings...")
            upsert_movie_rating_stats(cursor, rating_stats_df)
            print("Updated movie ratings!")

        elif file_type == 'embeddings':
            print("Downloading embeddings npy from S3...")
            embeddings = load_npy_from_s3(s3_client, bucket, key)
            print("Downloaded embeddings npy from S3!")

            if model_type == 'cold_start':
                staging_table = "movie_embedding_coldstart_staging"
                prod_table = "movie_embedding_coldstart_prod"
            else:
                staging_table = "movie_embedding_personalized_staging"
                prod_table = "movie_embedding_personalized_prod"

            metadata_key = f"movie_metadata/production/{version}/movie_metadata.csv"
            # Download metadata to get movie_ids in correct order
            print("Downloading metadata CSV from S3...")
            metadata_df = load_csv_from_s3(s3_client, bucket, metadata_key)
            print("Downloaded metadata CSV from S3!")

            print("loading embeddings to staging...")
            load_embeddings_to_staging(cursor, metadata_df , embeddings, staging_table)
            print("loaded embeddings to staging!")
            print("swapping tables...")
            swap_tables(cursor, staging_table, prod_table)
            print("swapped tabled!")
        
        conn.commit()

        cursor.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'{file_type} updated successfully',
                'version': version,
                'model_type': model_type
            })
        } 

    except Exception as e:
        print(f"Error: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn.close()
        raise Exception(f"Failed to update database: {str(e)}")