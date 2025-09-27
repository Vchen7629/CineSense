terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
        version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "us-west-1"
  access_key = var.aws-access-key
  secret_key = var.aws-secret-access-key
}