# helper functions for downloading model files from AWS s3
import boto3
from pathlib import Path
from utils.env_config import settings
import logging

logger = logging.getLogger(__name__)

# uses IAM role in prod, otherwise uses credentials
def get_s3_client():
    if settings.use_iam_role:
        logger.info("Using IAM role for S3 access")
        return boto3.client('s3', region_name=settings.aws_region)
    else:
        logger.info("Using AWS credentials for S3 access")
        return boto3.client(
            's3',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key,
            aws_secret_access_key=settings.aws_secret_access_key
        )

# download all recommendation model files from S3 to local directory
def download_recommendation_model_files():
    if not settings.production or not settings.s3_bucket_name:
        logger.info("Not in production mode or no S3 bucket name")
        return

    logger.info(f"Downloading model files from S3 Bucket: {settings.s3_bucket_name}")

    s3_client = get_s3_client()

    # create local directory for models
    local_model_dir = Path("/tmp/models")
    local_model_dir.mkdir(parents=True, exist_ok=True)

    model_files = [
        settings.user_tower_model_name,
        settings.movie_tower_model_name,
        settings.reranker_model_name,
        settings.genre_mlb_name
    ]

    for model_file in model_files:
        s3_key = f"{settings.s3_model_prefix}{model_file}"
        local_path = local_model_dir / model_file

        try:
            logger.info(f"Downloading {s3_key} to {local_path}")
            s3_client.download_file(
                Bucket=settings.s3_bucket_name,
                Key=s3_key,
                Filename=str(local_path)
            )
            logger.info(f"Downloaded {model_file}")
        except Exception as e:
            logger.error(f"Failed to download {model_file}: {e}")
            raise

    logger.info("All model files downloaded successfully")
