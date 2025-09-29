resource "aws_s3_bucket" "frontend" {
    bucket = var.s3-bucket-name

    tags = {
        ManagedBy = "Terraform"
    }

    #lifecycle {
    #    prevent_destroy = true
    #}
}

# Create OAI for CloudFront to access S3 bucket
resource "aws_cloudfront_origin_access_identity" "frontend_oai" {
  comment = "OAI for frontend S3 bucket"
}

resource "aws_s3_bucket_policy" "frontend" {
    bucket = aws_s3_bucket.frontend.id

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
            Effect    = "Allow"
            Principal = {
                AWS = aws_cloudfront_origin_access_identity.frontend_oai.iam_arn
            }
            Action    = ["s3:GetObject"]
            Resource  = "${aws_s3_bucket.frontend.arn}/*"
            }
        ]
    })
}

resource "aws_s3_bucket_public_access_block" "frontend" {
  bucket                  = aws_s3_bucket.frontend.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}