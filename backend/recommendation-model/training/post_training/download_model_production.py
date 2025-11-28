import boto3
import os
from utils.env_config import settings
from shared.path_config import path_helper
from typing import Optional, List

def list_available_versions() -> List[str]:
    """List all available model versions in S3"""
    s3_client = boto3.client(
        's3',
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key,
        aws_secret_access_key=settings.aws_secret_access_key
    )

    s3_bucket = settings.s3_bucket_name or 'cinesense-ml-artifacts-prod'
    prefix = "models/production/"

    try:
        response = s3_client.list_objects_v2(
            Bucket=s3_bucket,
            Prefix=prefix,
            Delimiter='/'
        )

        versions = []
        if 'CommonPrefixes' in response:
            for prefix_info in response['CommonPrefixes']:
                # Extract version from path like "models/production/v1.0.0/"
                version = prefix_info['Prefix'].split('/')[-2]
                versions.append(version)

        return sorted(versions, reverse=True)  # Newest first
    except Exception as e:
        print(f"Error listing versions: {e}")
        return []


def download_from_s3(model_version: str, large_dataset: bool = False) -> dict:
    """Download model files from S3 to local directory"""
    paths = path_helper(large_dataset=large_dataset)

    # Local file paths (where to save)
    local_files = {
        "user_tower.pth": paths.user_tower_model_path,
        "movie_tower.pth": paths.movie_tower_model_path,
        "reranker-model.txt": paths.reranker_model_path,
        "genre_mlb.joblib": paths.genre_mlb_path
    }

    # Create S3 client with credentials
    s3_client = boto3.client(
        's3',
        region_name=settings.aws_region,
        aws_access_key_id=settings.aws_access_key,
        aws_secret_access_key=settings.aws_secret_access_key
    )

    # S3 bucket and prefix
    s3_bucket = settings.s3_bucket_name or 'cinesense-ml-artifacts-prod'
    s3_prefix = f"models/production/{model_version}"

    print(f"\n{'='*60}")
    print(f"Downloading model files from S3")
    print(f"Bucket: {s3_bucket}")
    print(f"Version: {model_version}")
    print(f"{'='*60}\n")

    # Ensure local directories exist
    for local_path in local_files.values():
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

    downloaded_files = []
    failed_files = []

    # Download each file
    for s3_filename, local_path in local_files.items():
        s3_key = f"{s3_prefix}/{s3_filename}"

        print(f"Downloading {s3_filename}...")

        try:
            # Check if file exists in S3
            s3_client.head_object(Bucket=s3_bucket, Key=s3_key)

            # Download file
            s3_client.download_file(
                Bucket=s3_bucket,
                Key=s3_key,
                Filename=local_path
            )

            file_size = os.path.getsize(local_path) / (1024 * 1024)  # Size in MB
            print(f"✓ Downloaded {s3_filename} ({file_size:.2f} MB) to {local_path}")
            downloaded_files.append(s3_filename)

        except s3_client.exceptions.NoSuchKey:
            print(f"✗ {s3_filename} not found in S3")
            failed_files.append(s3_filename)
        except Exception as e:
            print(f"✗ Failed to download {s3_filename}: {e}")
            failed_files.append(s3_filename)

    print(f"\n{'='*60}")
    print(f"Successfully downloaded {len(downloaded_files)}/{len(local_files)} files")
    if failed_files:
        print(f"Failed files: {', '.join(failed_files)}")
    print(f"Version: {model_version}")
    print(f"{'='*60}\n")

    return {
        'version': model_version,
        'bucket': s3_bucket,
        'downloaded_files': downloaded_files,
        'failed_files': failed_files,
        's3_prefix': s3_prefix
    }


def download_latest_version(large_dataset: bool = False) -> Optional[dict]:
    """Download the latest model version from S3"""
    versions = list_available_versions()

    if not versions:
        print("No model versions found in S3")
        return None

    latest_version = versions[0]
    print(f"Latest version: {latest_version}")

    return download_from_s3(latest_version, large_dataset)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Download model files from S3')
    parser.add_argument('--version', type=str, help='Specific version to download (e.g., v1.0.0)')
    parser.add_argument('--list', action='store_true', help='List available versions')
    parser.add_argument('--latest', action='store_true', help='Download latest version')
    parser.add_argument('--large-dataset', action='store_true', help='Use large dataset paths')

    args = parser.parse_args()

    if args.list:
        print("\nAvailable versions:")
        versions = list_available_versions()
        for v in versions:
            print(f"  - {v}")
        print()

    elif args.latest:
        result = download_latest_version(large_dataset=args.large_dataset)
        if result:
            print(f"\nLatest model downloaded: {result['version']}")

    elif args.version:
        result = download_from_s3(args.version, large_dataset=args.large_dataset)
        print(f"\nModel version {result['version']} downloaded")

    else:
        parser.print_help()
        print("\nExamples:")
        print("  python download_model_production.py --list")
        print("  python download_model_production.py --latest")
        print("  python download_model_production.py --version v1.0.0")
