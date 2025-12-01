import subprocess
import os
from utils.get_aws_rds_credentials import get_db_credentials

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