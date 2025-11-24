data "cloudflare_zone" "main" {
    zone_id = var.cloudflare_zone_id
}

# ACM certificate validation records
resource "cloudflare_dns_record" "api_acm_validation" {
    zone_id = var.cloudflare_zone_id
    # Extract just the subdomain part, removing the base domain and trailing dot
    name    = trimsuffix(replace(tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_name, ".cinesense.tech.", ""), ".")
    type    = tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_type
    content = trimsuffix(tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_value, ".")
    ttl     = 300
    proxied = false
}

# Point api.cinesense.tech to API Gateway
resource "cloudflare_dns_record" "api" {
    zone_id = var.cloudflare_zone_id
    name    = "api" 
    type    = "CNAME"
    content = aws_apigatewayv2_domain_name.api.domain_name_configuration[0].target_domain_name
    ttl     = 1
    proxied = false  
    
    depends_on = [aws_apigatewayv2_domain_name.api]
}