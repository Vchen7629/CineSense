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

provider "aws" {
  region = "us-west-1"
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}