# cloudwatch for monitoring

resource "aws_cloudwatch_log_group" "api_gateway" {
    name                = "/aws/apigateway/cinesense-api"
    retention_in_days   = 7
}

resource "aws_cloudwatch_log_group" "ecs_recommendation" {
    name                = "/ecs/recommendation-api" 
    retention_in_days   = 7
}

resource "aws_cloudwatch_log_group" "ecs_auth" {
    name                = "/ecs/auth-api" 
    retention_in_days   = 7
}
