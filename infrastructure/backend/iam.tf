
# Read/Download access for ecs task so docker container can
# read/download model files
resource "aws_iam_policy" "ecs_s3_policy" {
    name = "ModelFilesReadOnly"
    description = "Read/Download permissions ecs task to access model files "

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = [
                    "s3:GetObject",
                    "s3:ListBucket"
                ]
                Effect = "Allow"
                Resource = [
                    aws_s3_bucket.model_files.arn,
                    "${aws_s3_bucket.model_files.arn}/*"
                ]
            }
        ]
    })
}

resource "aws_iam_role" "recommendation_task_role" {
    name = "RecommendationTaskRole"

    assume_role_policy = jsonencode({
        Version         = "2012-10-17"
        Statement       = [{
            Effect      = "Allow"
            Principal   = {
                Service = "ecs-tasks.amazonaws.com"
            }
            Action      = "sts:AssumeRole"
        }]
    })
}

resource "aws_iam_role_policy_attachment" "recommendation_task_s3_attach" {
    role        = aws_iam_role.recommendation_task_role.id
    policy_arn  = aws_iam_policy.ecs_s3_policy.arn
}

# role allowing ECS to pull images from ECR and write Logs to CloudWatch
resource "aws_iam_role" "ecs_task_execution_role" {
    name = "ecsTaskExecutionRole"

    assume_role_policy = jsonencode({
        Version     = "2012-10-17"
        Statement   = [
            {
                Effect      = "Allow"
                Principal   = {
                    Service = "ecs-tasks.amazonaws.com"
                }
                Action      = "sts:AssumeRole"
            }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# role allowing EC2 to register with ECS
resource "aws_iam_role" "ecs_instance_role" {
  name = "ecsInstanceRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = { Service = "ec2.amazonaws.com" }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_instance_role_attach" {
  role                  = aws_iam_role.ecs_instance_role.name
  policy_arn            = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

# Instance profile for EC2 instances
resource "aws_iam_instance_profile" "ecs_instance_profile" {
    name                = "ecsInstanceProfile"
    role                = aws_iam_role.ecs_instance_role.name
}

resource "aws_iam_role" "lambda_migration_role" {
    name                = "cinesense-lambda-migration-role"

    assume_role_policy = jsonencode({
        Version         = "2012-10-17"
        Statement       = [{
            Effect      = "Allow"
            Principal   = {
                Service = "lambda.amazonaws.com"
            }
            Action      = "sts:AssumeRole"
        }]
    })
}

# attach basic lambda execution role to lambda migration role
resource "aws_iam_role_policy_attachment" "lambda_basic" {
    role                = aws_iam_role.lambda_migration_role.name
    policy_arn          = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" 
}

# attach VPC execution role to lambda migration role
resource "aws_iam_role_policy_attachment" "lambda_vpcs" {
    role       = aws_iam_role.lambda_migration_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# iam role to allow api gateway to log to cloudwatch
resource "aws_iam_role" "api_gateway_cloudwatch" {
    name = "api-gateway-cloudwatch-global"
    
    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
            Effect = "Allow"
            Principal = {
                Service = "apigateway.amazonaws.com"
            }
            Action = "sts:AssumeRole"
        }]
    })
}

resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch" {
    role       = aws_iam_role.api_gateway_cloudwatch.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

# Policy for reading secrets
resource "aws_iam_policy" "ecs_secrets_policy" {
    name        = "CineSenseSecretsReadPolicy"
    description = "Allow ECS tasks to read database credentials"

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [{
            Effect = "Allow"
            Action = [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret"
            ]
            Resource = [
                aws_secretsmanager_secret.db_credentials.arn
            ]
        }]
    })
}

resource "aws_iam_role_policy_attachment" "execution_secrets" {
    role       = aws_iam_role.ecs_task_execution_role.name
    policy_arn = aws_iam_policy.ecs_secrets_policy.arn
}

# Attach to recommendation task role
resource "aws_iam_role_policy_attachment" "recommendation_secrets" {
    role       = aws_iam_role.recommendation_task_role.name
    policy_arn = aws_iam_policy.ecs_secrets_policy.arn
}

# Attach to Lambda migration role
resource "aws_iam_role_policy_attachment" "lambda_secrets" {
    role       = aws_iam_role.lambda_migration_role.name
    policy_arn = aws_iam_policy.ecs_secrets_policy.arn
}