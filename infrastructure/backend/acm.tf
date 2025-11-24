resource "aws_acm_certificate" "api" {
    domain_name       = "api.cinesense.tech"
    validation_method = "DNS"

    lifecycle {
        create_before_destroy = true
    }

    tags = {
        Name = "cinesense-api-cert"
    }
}

# validate record
resource "aws_acm_certificate_validation" "api_cert_validation" {
    certificate_arn         = aws_acm_certificate.api.arn
    validation_record_fqdns = [
        trimsuffix(tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_name, ".")
    ]
    depends_on              = [cloudflare_dns_record.api_acm_validation]
}