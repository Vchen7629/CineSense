# api gateway sitting between frontend and fastapi backend
resource "aws_apigatewayv2_api" "main" {
    name          = "cinesense-api"
    protocol_type = "HTTP"

    cors_configuration {
        allow_origins   = ["https://cinesense.tech", "https://www.cinesense.tech"]
        allow_methods   = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        allow_headers   = ["content-type", "authorization", "x-requested-with", "accept", "origin", "access-control-request-method", "access-control-request-headers"]
        expose_headers  = ["*"]
        allow_credentials = true
        max_age         = 300
    }
}

# integrate with public ALB
resource "aws_apigatewayv2_integration" "alb" {
    api_id                  = aws_apigatewayv2_api.main.id
    integration_type        = "HTTP_PROXY"
    integration_uri         = "http://${aws_lb.main.dns_name}/{proxy}" 
    integration_method      = "ANY"

    request_parameters = {
        "overwrite:path" = "$request.path"
    }
}

# routing all requests to ALB
resource "aws_apigatewayv2_route" "default" {
    api_id      = aws_apigatewayv2_api.main.id
    route_key   = "ANY /{proxy+}"
    target      = "integrations/${aws_apigatewayv2_integration.alb.id}" 
}

# Production stage with auto-deploy
resource "aws_apigatewayv2_stage" "prod" {
    api_id      = aws_apigatewayv2_api.main.id
    name        = "$default"
    auto_deploy = true

    access_log_settings {
        destination_arn = aws_cloudwatch_log_group.api_gateway.arn
        format = jsonencode({
            requestId      = "$context.requestId"
            ip             = "$context.identity.sourceIp"
            requestTime    = "$context.requestTime"
            httpMethod     = "$context.httpMethod"
            routeKey       = "$context.routeKey"
            status         = "$context.status"
            protocol       = "$context.protocol"
            responseLength = "$context.responseLength"
        })
    }
}

# custom domain for api gateway
resource "aws_apigatewayv2_domain_name" "api" {
    domain_name = "api.cinesense.tech"

    domain_name_configuration {
        certificate_arn = aws_acm_certificate.api.arn
        endpoint_type   = "REGIONAL"
        security_policy = "TLS_1_2"
    }
}


resource "aws_apigatewayv2_api_mapping" "api" {
      api_id      = aws_apigatewayv2_api.main.id
      domain_name = aws_apigatewayv2_domain_name.api.id
      stage       = aws_apigatewayv2_stage.prod.id
}

# for permissions to write logs to cloudwatch
resource "aws_api_gateway_account" "main" {
    cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch.arn
}
