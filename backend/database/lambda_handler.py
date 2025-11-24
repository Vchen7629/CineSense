import subprocess
import os
import json
import boto3
from botocore.exceptions import ClientError

# Fetch database credentials from AWS Secrets Manager.
def get_db_credentials():
    secret_name = "cinesense/db/credentials_v2"
    region_name = "us-west-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise Exception(f"Failed to retrieve secret: {e}")

    # Parse the secret JSON
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret

# Lambda handle that runs Alembic migrations
def handler(event, context):
    try:
        # Fetch DB credentials from Secrets Manager
        db_creds = get_db_credentials()

        # Build DATABASE_URL for Alembic
        database_url = (
            f"postgresql://{db_creds['username']}:{db_creds['password']}"
            f"@{db_creds['host']}:{db_creds['port']}/{db_creds['dbname']}"
        )

        # Set environment variables for Alembic and UV
        env = {
            **os.environ,
            'DATABASE_URL': database_url,
            'UV_CACHE_DIR': '/tmp/.uv-cache'
        }

        # Run alembic upgrade
        result = subprocess.run(
            ["uv", "run", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
            env=env
        )

        if result.stderr:
            print("Warnings:")
            print(result.stderr)
        
        return {
            'statusCode': 200,
            'body': 'Migrations completed successfully'
        }
    except subprocess.CalledProcessError as e:
        print("Migration failed")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")

        raise Exception(f"Migration failed: {e.stderr}")