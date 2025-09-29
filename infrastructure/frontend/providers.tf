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
}

provider "aws" {
  region = "us-west-1"
  access_key = var.aws-access-key
  secret_key = var.aws-secret-access-key
}

provider "aws" {
  alias  = "use1"
  region = "us-east-1"
}

provider "cloudflare" {
  api_token = var.cloudflare-api-token
}