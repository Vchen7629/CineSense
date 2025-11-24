output "model_files_bucket_name" {
    value = aws_s3_bucket.model_files.bucket
}

output "model_files_bucket_arn" {
    value = aws_s3_bucket.model_files.arn
}

# output for github actions
output "migration_lambda_name" {
    value       = aws_lambda_function.db_migration.function_name
    description = "Lambda function name for migrations"
}

output "api_gateway_endpoint" {
    value       = aws_apigatewayv2_api.main.api_endpoint
    description = "API Gateway endpoint URL"
}

output "api_gateway_custom_domain" {
    value       = "https://api.cinesense.com"
    description = "Custom domain for API"
}