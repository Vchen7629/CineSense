# This requests acm certifcate for the domain
resource "aws_acm_certificate" "frontend_cert" {
  provider = aws.use1
  domain_name       = var.domain-name
  validation_method = "DNS"

  tags = {
    ManagedBy = "Terraform"
  }
}

# Since im using cloudflare i need to add a txt record
resource "cloudflare_dns_record" "acm_validation" {
  zone_id = var.cloudflare-zone-id
  name    = tolist(aws_acm_certificate.frontend_cert.domain_validation_options)[0].resource_record_name
  type    = tolist(aws_acm_certificate.frontend_cert.domain_validation_options)[0].resource_record_type
  content = tolist(aws_acm_certificate.frontend_cert.domain_validation_options)[0].resource_record_value
  ttl     = 300
  proxied = false
}

# Point www.cinesense.tech to CloudFront
resource "cloudflare_dns_record" "frontend_cname" {
  zone_id = var.cloudflare-zone-id
  name    = "www"
  type    = "CNAME"
  content = aws_cloudfront_distribution.frontend_cdn.domain_name
  ttl     = 1
  proxied = true # or false if you want to bypass Cloudflare
}

# This validates the certificate using the txt record created above
resource "aws_acm_certificate_validation" "frontend_cert_validation" {
  provider = aws.use1
  certificate_arn         = aws_acm_certificate.frontend_cert.arn
  validation_record_fqdns = [cloudflare_dns_record.acm_validation.name]
  depends_on = [cloudflare_dns_record.acm_validation]
}
