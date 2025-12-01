import boto3
from botocore.exceptions import ClientError
import json

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
