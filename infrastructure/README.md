# Infrastructure Terraform code

terraform code to scaffold project infrastructure on AWS.

## Dependencies
You will need the following files

1. Credentials file in your .aws folder
```bash
[default]
aws_access_key_id = <your-aws-iam-user-access-token>
aws_secret_access_key = <your-aws-iam-user-secret-key>
```

and also the terraform.tfvars file in the backend 
```bash
db_username = <your-aws-rds-database-username>
db_password = <your-aws-rds-database-password>
cloudflare_api_token = <your-cloudflare-account-api-token>
cloudflare_zone_id = <your-cloudflare-domain-zone-id>
```

Note: cloudflare_api_token needs dns:edit for your cloudflare domain

## Setup

### Backend

1. To set up the backend first comment out the backend so it creates everything

```bash
terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 6.0"
    }
    cloudflare = {
        source = "cloudflare/cloudflare"
        version = "~> 5.0"
    }
  }

  #backend "s3" {
  #    bucket  = "cinesense-backend-tf-state-files"
  #    key     = "terraform.tfstate"
  #    region  = "us-west-1"
  #    encrypt = true
  #}
}
```

2. run terraform commands to create just the terraform state s3 file
```bash
terraform init

terraform apply \
    -target=aws_s3_bucket.terraform_state_files \
    -target=aws_s3_bucket_versioning.terraform_state_files_versioning \
    -target=aws_s3_bucket_server_side_encryption_configuration.terraform_state_files_encryption \
    -target=aws_s3_bucket_public_access_block.terraform_state_files_private

```

3. After its done, uncomment the backend in providers and migrate state

```bash
terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 6.0"
    }
    cloudflare = {
        source = "cloudflare/cloudflare"
        version = "~> 5.0"
    }
  }

  backend "s3" {
      bucket  = "cinesense-backend-tf-state-files"
      key     = "terraform.tfstate"
      region  = "us-west-1"
      encrypt = true
  }
}

terraform init --migrate-state
```

4. Create the rest of the infrastructure
```bash
terraform apply
```

## State File
Terraform State (file that terraform uses to manage the infrastructure) is stored on an AWS S3 bucket for best practices

```bash
terraform init 
```

Now you can use the state file from s3 to destroy or modify the infrastructure
