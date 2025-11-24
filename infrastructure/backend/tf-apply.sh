#!/bin/bash
# Helper script to run terraform with AWS credentials exported

# Extract credentials from ~/.aws/credentials
export AWS_ACCESS_KEY_ID=$(grep aws_access_key_id ~/.aws/credentials | head -1 | cut -d'=' -f2 | tr -d ' "')
export AWS_SECRET_ACCESS_KEY=$(grep aws_secret_access_key ~/.aws/credentials | head -1 | cut -d'=' -f2 | tr -d ' "')
export AWS_REGION="us-west-1"

echo "AWS credentials loaded from ~/.aws/credentials"
echo "Running terraform $@"

# Run terraform with whatever arguments were passed
terraform "$@"
