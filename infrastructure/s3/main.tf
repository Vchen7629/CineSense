resource "aws_s3_bucket" "frontend" {
    bucket = var.s3-bucket-name

    tags = {
        ManagedBy = "Terraform"
    }

    lifecycle {
        prevent_destroy = true
    }
}

resource "aws_s3_bucket_website_configuration" "frontend" {
    bucket = aws_s3_bucket.frontend.id

    index_document {
      suffix = "index.html"
    }

    error_document {
      key = "index.html"
    }
}

resource "aws_s3_bucket_policy" "frontend" {
    bucket = aws_s3_bucket.frontend.id

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
            Effect    = "Allow"
            Principal = "*"
            Action    = ["s3:GetObject"]
            Resource  = "${aws_s3_bucket.frontend.arn}/*"
            }
        ]
    })
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}