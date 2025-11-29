import boto3
import os
from datetime import datetime
from utils.env_config import settings
from shared.path_config import path_helper

# Upload model files to s3 bucket for use in production ecr containers
# Note: Need all model files before running this
def save_to_s3(model_version: str = None):
    paths = path_helper(large_dataset=False)

    # Local file paths
    movie_tower_file_path = paths.movie_tower_model_path
    user_tower_file_path = paths.user_tower_model_path
    reranker_model_file_path = paths.reranker_model_path
    genre_mlb_path = paths.genre_mlb_path

    # Create S3 client with credentials
    s3_client = boto3.client(
        's3',
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key,
        aws_secret_access_key=settings.aws_secret_access_key
    )

    # Generate version tag if not provided
    if model_version is None:
        model_version = datetime.now().strftime('%Y%m%d-%H%M%S')

    # S3 bucket and prefix
    s3_bucket = settings.s3_bucket_name or 'cinesense-ml-artifacts-prod'
    s3_prefix = f"models/production/{model_version}"

    print(f"\n{'='*60}")
    print(f"Uploading model files to S3")
    print(f"Bucket: {s3_bucket}")
    print(f"Version: {model_version}")
    print(f"{'='*60}\n")

    # List of files to upload
    files_to_upload = [
        (user_tower_file_path, "user_tower.pth"),
        (movie_tower_file_path, "movie_tower.pth"),
        (reranker_model_file_path, "reranker-model.txt"),
        (genre_mlb_path, "genre_mlb.joblib")
    ]

    uploaded_files = []

    # Upload each file
    for local_path, s3_filename in files_to_upload:
        if not os.path.exists(local_path):
            print(f"Warning: {s3_filename} not found at {local_path}")
            continue

        s3_key = f"{s3_prefix}/{s3_filename}"
        file_size = os.path.getsize(local_path) / (1024 * 1024)  # Size in MB

        print(f"Uploading {s3_filename} ({file_size:.2f} MB)...")

        try:
            s3_client.upload_file(
                Filename=local_path,
                Bucket=s3_bucket,
                Key=s3_key,
                ExtraArgs={'ServerSideEncryption': 'AES256'}  # Match bucket encryption
            )
            print(f"Uploaded to s3://{s3_bucket}/{s3_key}")
            uploaded_files.append(s3_filename)
        except Exception as e:
            print(f"Failed to upload {s3_filename}: {e}")
            raise

    print(f"\n{'='*60}")
    print(f"Successfully uploaded {len(uploaded_files)}/{len(files_to_upload)} files")
    print(f"Version: {model_version}")
    print(f"{'='*60}\n")

    return {
        'version': model_version,
        'bucket': s3_bucket,
        'uploaded_files': uploaded_files,
        's3_prefix': s3_prefix
    }


if __name__ == "__main__":
    result = save_to_s3(model_version="v1")
    print(f"\nModel files uploaded to: s3://{result['bucket']}/{result['s3_prefix']}/")
