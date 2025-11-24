resource "aws_security_group" "alb" {
  name          = "cinesense-alb-sg"
  description   = "Security group for Application Load Balancer"
  vpc_id        = aws_vpc.main.id

  tags = {
    Name        = "cinesense-alb-sg"
  }
}

resource "aws_security_group" "ecs_tasks" {
  name          = "cinesense-ecs-tasks-sg"
  description   = "Security group for ECS tasks"
  vpc_id        = aws_vpc.main.id

  tags = {
    Name        = "cinesense-ecs-tasks-sg"
  }
}

resource "aws_security_group" "rds" {
  name          = "cinesense-rds-sg"
  description   = "Security group for RDS PostgreSQL"
  vpc_id        = aws_vpc.main.id

  tags = {
    Name        = "cinesense-rds-sg"
  }
}

resource "aws_security_group" "lambda_migration" {
  name          = "cinesense-lambda-migration-sg"
  description   = "Security group for Lambda migration function"
  vpc_id        = aws_vpc.main.id

  tags = {
    Name        = "cinesense-lambda-migration-sg"
  }
}

resource "aws_security_group" "vpc_endpoints" {
  name          = "cinesense-vpc-endpoints-sg"
  description   = "Security group for VPC endpoints"
  vpc_id        = aws_vpc.main.id

  tags = {
    Name        = "cinesense-vpc-endpoints-sg"
  }
}

resource "aws_security_group" "ec2_instances" {
  name              = "cinesense-ec2-sg"
  description       = "Security group for EC2 instances"
  vpc_id            = aws_vpc.main.id

  tags = {
    Name            = "cinesense-ec2-sg"
  }
}

# Data source for CloudFront managed prefix list
data "aws_ec2_managed_prefix_list" "cloudfront" {
    name            = "com.amazonaws.global.cloudfront.origin-facing"
}

# ALB rules
resource "aws_security_group_rule" "alb_ingress_http" {
    type                        = "ingress"
    from_port                   = 80
    to_port                     = 80
    protocol                    = "tcp"
    cidr_blocks                 = ["0.0.0.0/0"]
    security_group_id           = aws_security_group.alb.id
    description                 = "Allow HTTP from API Gateway"
}

resource "aws_security_group_rule" "alb_ingress_https" {
    type                        = "ingress"
    from_port                   = 443
    to_port                     = 443
    protocol                    = "tcp"
    cidr_blocks                 = ["0.0.0.0/0"]
    security_group_id           = aws_security_group.alb.id
    description                 = "Allow HTTPS from CloudFront"
}

resource "aws_security_group_rule" "alb_egress_ecs" {
    type                        = "egress"
    from_port                   = 8000
    to_port                     = 8000
    protocol                    = "tcp"
    source_security_group_id    = aws_security_group.ecs_tasks.id
    security_group_id           = aws_security_group.alb.id
    description                 = "Allow traffic to ECS tasks only"
}

# ecs tasks security group rules
resource "aws_security_group_rule" "ecs_ingress_alb" {
    type                        = "ingress"
    from_port                   = 8000
    to_port                     = 8000
    protocol                    = "tcp"
    source_security_group_id    = aws_security_group.alb.id
    security_group_id           = aws_security_group.ecs_tasks.id
    description                 = "Allow traffic to ECS tasks only"
}

resource "aws_security_group_rule" "ecs_ingress_self" {
  type                          = "ingress"
  from_port                     = 8000
  to_port                       = 8000
  protocol                      = "tcp"
  self                          = true
  security_group_id             = aws_security_group.ecs_tasks.id
  description                   = "Allow inter-service communication on port 8000"
}

resource "aws_security_group_rule" "ecs_egress_vpc_endpoints" {
  type                          = "egress"
  from_port                     = 443
  to_port                       = 443
  protocol                      = "tcp"
  source_security_group_id      = aws_security_group.vpc_endpoints.id
  security_group_id             = aws_security_group.ecs_tasks.id
  description                   = "Allow HTTPS to VPC endpoints"
}

resource "aws_security_group_rule" "ecs_egress_rds" {
  type                          = "egress"
  from_port                     = 5432
  to_port                       = 5432
  protocol                      = "tcp"
  source_security_group_id      = aws_security_group.rds.id
  security_group_id             = aws_security_group.ecs_tasks.id
  description                   = "Allow access to RDS"
}

resource "aws_security_group_rule" "ecs_egress_dns" {
  type                          = "egress"
  from_port                     = 53
  to_port                       = 53
  protocol                      = "udp"
  cidr_blocks                   = ["0.0.0.0/0"]
  security_group_id             = aws_security_group.ecs_tasks.id
  description                   = "Allow DNS resolution"
}

# rds security group rules
resource "aws_security_group_rule" "rds_ingress_ecs" {
  type                          = "ingress"
  from_port                     = 5432
  to_port                       = 5432
  protocol                      = "tcp"
  source_security_group_id      = aws_security_group.ecs_tasks.id
  security_group_id             = aws_security_group.rds.id
  description                   = "Allow PostgreSQL access from ECS tasks"
}

resource "aws_security_group_rule" "rds_ingress_lambda" {
  type                          = "ingress"
  from_port                     = 5432
  to_port                       = 5432
  protocol                      = "tcp"
  source_security_group_id      = aws_security_group.lambda_migration.id
  security_group_id             = aws_security_group.rds.id
  description                   = "Allow PostgreSQL from Lambda migrations"
}

resource "aws_security_group_rule" "rds_egress_all" {
  type                      = "egress"
  from_port                 = 0
  to_port                   = 0
  protocol                  = "-1"
  cidr_blocks               = ["0.0.0.0/0"]
  security_group_id         = aws_security_group.rds.id
  description               = "Allow outbound for managed service"
}

# ec2 instance security groups
resource "aws_security_group_rule" "ec2_ingress_alb" {
  type                      = "ingress"
  from_port                 = 32768
  to_port                   = 65535
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.alb.id
  security_group_id         = aws_security_group.ec2_instances.id
  description               = "Allow dynamic port mapping from ALB"
}

resource "aws_security_group_rule" "ec2_egress_vpc_endpoints" {
  type                      = "egress"
  from_port                 = 443
  to_port                   = 443
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.vpc_endpoints.id
  security_group_id         = aws_security_group.ec2_instances.id
  description               = "Allow HTTPS to VPC endpoints for ECS agent, ECR, CloudWatch"
}

resource "aws_security_group_rule" "ec2_egress_dns" {
  type                      = "egress"
  from_port                 = 53
  to_port                   = 53
  protocol                  = "udp"
  cidr_blocks               = ["0.0.0.0/0"]
  security_group_id         = aws_security_group.ec2_instances.id
  description               = "Allow DNS resolution"
}

# vpc endpoints security group rules
resource "aws_security_group_rule" "vpc_endpoints_ingress_ecs" {
  type                      = "ingress"
  from_port                 = 443
  to_port                   = 443
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.ecs_tasks.id
  security_group_id         = aws_security_group.vpc_endpoints.id
  description               = "Allow HTTPS from ECS tasks"
}

resource "aws_security_group_rule" "vpc_endpoints_ingress_ec2" {
  type                      = "ingress"
  from_port                 = 443
  to_port                   = 443
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.ec2_instances.id
  security_group_id         = aws_security_group.vpc_endpoints.id
  description               = "Allow HTTPS from EC2 instances"
}

resource "aws_security_group_rule" "vpc_endpoints_ingress_lambda" {
  type                      = "ingress"
  from_port                 = 443
  to_port                   = 443
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.lambda_migration.id
  security_group_id         = aws_security_group.vpc_endpoints.id
  description               = "Allow HTTPS from Lambda"
}

resource "aws_security_group_rule" "vpc_endpoints_egress_all" {
  type                      = "egress"
  from_port                 = 0
  to_port                   = 0
  protocol                  = "-1"
  cidr_blocks               = ["0.0.0.0/0"]
  security_group_id         = aws_security_group.vpc_endpoints.id
  description               = "Allow all outbound traffic"
}

# Lambda Migration Security Group Rules
resource "aws_security_group_rule" "lambda_egress_rds" {
  type                      = "egress"
  from_port                 = 5432
  to_port                   = 5432
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.rds.id
  security_group_id         = aws_security_group.lambda_migration.id
  description               = "Allow PostgreSQL access from Lambda"
}

resource "aws_security_group_rule" "lambda_egress_vpc_endpoints" {
  type                      = "egress"
  from_port                 = 443
  to_port                   = 443
  protocol                  = "tcp"
  source_security_group_id  = aws_security_group.vpc_endpoints.id
  security_group_id         = aws_security_group.lambda_migration.id
  description               = "Allow HTTPS to VPC endpoints"
}

resource "aws_security_group_rule" "lambda_egress_dns" {
  type                      = "egress"
  from_port                 = 53
  to_port                   = 53
  protocol                  = "udp"
  cidr_blocks               = ["0.0.0.0/0"]
  security_group_id         = aws_security_group.lambda_migration.id
  description               = "Allow DNS"
}