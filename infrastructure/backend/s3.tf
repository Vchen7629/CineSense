# s3 table for versioned offline trained movie embeddings
resource "aws_s3_bucket" "model_files" {
    bucket            = var.aws-model-file-s3-name

    force_destroy     = false

    tags = {
      Name            = var.aws-model-file-s3-name
      Environment     = "Production"
    }
}

# s3 bucket for storing backend terraform state files
resource "aws_s3_bucket" "terraform_state_files" {
    bucket            = "cinesense-backend-tf-state-files"

    force_destroy     = false

    lifecycle {
        prevent_destroy = true
    }

    tags = {
        Name          = "terraform"
        Environment   = "Production"
    }
}

# Private Buckets
resource "aws_s3_bucket_public_access_block" "model_files_private" {
    bucket                  = aws_s3_bucket.model_files.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "terraform_state_files_private" {
    bucket = aws_s3_bucket.terraform_state_files.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}

# Enable Versioning for buckets
resource "aws_s3_bucket_versioning" "model_files_versioning" {
    bucket = aws_s3_bucket.model_files.id

    versioning_configuration {
      status = "Enabled"
    }
}

resource "aws_s3_bucket_versioning" "terraform_state_files_versioning" {
    bucket = aws_s3_bucket.terraform_state_files.id

    versioning_configuration {
      status = "Enabled"
    }
}

# Enable Encryption for buckets
resource "aws_s3_bucket_server_side_encryption_configuration" "model_files_encryption" {
    bucket = aws_s3_bucket.model_files.id

    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_files_encryption" {
    bucket = aws_s3_bucket.terraform_state_files.id

    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
}