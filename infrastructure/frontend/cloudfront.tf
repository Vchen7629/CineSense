resource "aws_cloudfront_distribution" "frontend_cdn" {
    origin {
        domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
        origin_id   = "S3-frontend-origin"

        s3_origin_config {
          origin_access_identity = aws_cloudfront_origin_access_identity.frontend_oai.cloudfront_access_identity_path
        }
    }
    
    enabled             = true
    comment             = "CDN for Frontend S3 Bucket"
    default_root_object = "index.html"
    price_class = "PriceClass_100" # Use only US, Canada and Europe edge locations
    
    default_cache_behavior {
        allowed_methods  = ["GET", "HEAD"]
        cached_methods   = ["GET", "HEAD"]
        target_origin_id = "S3-frontend-origin"
    
        viewer_protocol_policy = "redirect-to-https"

        cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    }
    
    restrictions {
        geo_restriction {
        restriction_type = "none"
        }
    }
    
    # This attaches the acm certificate to cloudfront dist
    viewer_certificate {
        acm_certificate_arn = aws_acm_certificate_validation.frontend_cert_validation.certificate_arn
        ssl_support_method  = "sni-only"
        minimum_protocol_version = "TLSv1.2_2021"
    }
    
    tags = {
        ManagedBy = "Terraform"
    }
}