# ecs infrastructure to deploy fastapi docker containers to

# ecs cluster for cinesense backend fastapi containers to run on
resource "aws_ecs_cluster" "cinesense" {
    name = "cinesense-cluster"
}

# container configs for recommendation fastapi ecs running on ec2
resource "aws_ecs_task_definition" "recommendation" {
    family = "cinesense-recommendation-task"
    network_mode = "awsvpc"
    region = "us-west-1"

    # less than t3.medium ec2 limits to leave room for os
    cpu     = "1792" # 2 vCPU
    memory  = "3072" # 3 GB

    task_role_arn       = aws_iam_role.recommendation_task_role.arn
    execution_role_arn  = aws_iam_role.ecs_task_execution_role.arn

    container_definitions = jsonencode([
        {
            name        = "recommendation-api"
            image       = "${aws_ecr_repository.recommendation_api.repository_url}:latest"
            essential   = true

            portMappings = [
                {
                    containerPort = 8000
                    hostPort      = 8000 
                    protocol      = "tcp"
                }
            ]

            logConfiguration = {
                logDriver = "awslogs"
                options = {
                    "awslogs-group"         = aws_cloudwatch_log_group.ecs_recommendation.name
                    "awslogs-region"        = "us-west-1"
                    "awslogs-stream-prefix" = "ecs"
                }
            }

            secrets = [
                {
                    name        = "DB_USERNAME"
                    valueFrom   = "${aws_secretsmanager_secret.db_credentials.arn}:username::"
                },
                {
                    name      = "DB_PASSWORD"
                    valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:password::"
                },
                {
                    name      = "DB_HOST"
                    valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:host::"
                },
                {
                    name      = "DB_PORT"
                    valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:port::"
                },
                {
                    name      = "DB_NAME"
                    valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:dbname::"
                }
            ]

            environment = [
                {
                    name    = "production"
                    value   = "true"
                },
                {
                    name    = "embedding_dim"
                    value   = "512"
                },
                {
                    name    = "aws_region"
                    value   = "us-west-1"
                },
                {
                    name    = "use_iam_role"
                    value   = "true"
                },
                {
                    name    = "s3_bucket_name"
                    value   = var.aws-model-file-s3-name
                },
                {
                    name    = "s3_model_prefix"
                    value   = "models/production/v1/"
                },
                {
                    name    = "log_level"
                    value   = "INFO"
                },
                {
                    name    = "cors_origins"
                    value   = "[\"https://cinesense.tech\",\"https://www.cinesense.tech\"]"
                }
            ]
        }
    ])
}

# container config for user auth fastapi ecs running on ec2
resource "aws_ecs_task_definition" "user-auth" {
    family = "cinesense-auth-task"
    network_mode = "awsvpc"
    region = "us-west-1"

    cpu     = "1024" # 1 vCPU
    memory  = "768" 

    execution_role_arn = aws_iam_role.ecs_task_execution_role.arn

    container_definitions = jsonencode([
        {
            name        = "auth-api"
            image       = "${aws_ecr_repository.auth_api.repository_url}:latest"
            essential   = true

            portMappings = [
                {
                    containerPort = 8001
                    hostPort      = 8001
                    protocol      = "tcp"
                }
            ]

            logConfiguration = {
                logDriver = "awslogs"
                options = {
                    "awslogs-group"         = aws_cloudwatch_log_group.ecs_auth.name
                    "awslogs-region"        = "us-west-1"
                    "awslogs-stream-prefix" = "ecs"
                }
            }

            secrets = [
                {
                    name        = "DB_USERNAME"
                    valueFrom   = "${aws_secretsmanager_secret.db_credentials.arn}:username::"
                },
                {
                    name      = "DB_PASSWORD"
                    valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:password::"
                },
                {
                    name      = "DB_HOST"
                    valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:host::"
                },
                {
                    name      = "DB_PORT"
                    valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:port::"
                },
                {
                    name      = "DB_NAME"
                    valueFrom = "${aws_secretsmanager_secret.db_credentials.arn}:dbname::"
                }
            ]

            environment = [
                {
                    name    = "log_level"
                    value   = "INFO"
                },
                {
                    name    = "cors_origins"
                    value   = "[\"https://cinesense.tech\",\"https://www.cinesense.tech\"]"
                }
            ]
        }
    ])
}

# services to tell tasks to run on the cluster
resource "aws_ecs_service" "recommendation" {
    name                    = "recommendation-service"
    cluster                 = aws_ecs_cluster.cinesense.id
    task_definition         = aws_ecs_task_definition.recommendation.arn
    desired_count           = 1
    force_new_deployment    = true
    deployment_maximum_percent         = 200
    deployment_minimum_healthy_percent = 0

    # Give the app time to download models and start (5 minutes)
    health_check_grace_period_seconds = 300

    # to make sure it runs on t3.medium
    capacity_provider_strategy {
        capacity_provider = aws_ecs_capacity_provider.recommendation.name
        weight           = 1
        base             = 1
    }

    network_configuration { 
        subnets             = [aws_subnet.private.id]
        security_groups     = [aws_security_group.ecs_tasks.id]
        assign_public_ip    = false
    }

    load_balancer {
        target_group_arn    = aws_lb_target_group.recommendation.arn
        container_name      = "recommendation-api"
        container_port      = 8000    
    }

    depends_on = [aws_lb_listener.http]
}

resource "aws_ecs_service" "user-auth" {
    name            = "auth-service"
    cluster         = aws_ecs_cluster.cinesense.id
    task_definition         = aws_ecs_task_definition.user-auth.arn
    desired_count           = 1
    force_new_deployment    = true
    deployment_maximum_percent         = 200
    deployment_minimum_healthy_percent = 0

    # to make sure it runs on t3a.micro
    capacity_provider_strategy {
        capacity_provider = aws_ecs_capacity_provider.auth.name
        weight           = 1
        base             = 1
    }

    network_configuration {
        subnets          = [aws_subnet.private.id]
        security_groups  = [aws_security_group.ecs_tasks.id]
        assign_public_ip = false
    }

    load_balancer {
        target_group_arn    = aws_lb_target_group.auth.arn
        container_name      = "auth-api"
        container_port      = 8001    
    }

    depends_on = [aws_lb_listener.http]
}

# capacity provider to register autoscaling group defined for ec2s with ecs
resource "aws_ecs_capacity_provider" "recommendation" {
    name                        = "cinesense-recommendation-capacity-provider"

    auto_scaling_group_provider {
        auto_scaling_group_arn  = aws_autoscaling_group.ecs_asg_recommendations.arn

        managed_scaling {
            status              = "ENABLED"
            target_capacity     = 100
        }
    }
}

resource "aws_ecs_capacity_provider" "auth" {
    name                        = "cinesense-auth-capacity-provider"

    auto_scaling_group_provider {
        auto_scaling_group_arn  = aws_autoscaling_group.ecs_asg_auth.arn

        managed_scaling {
            status              = "ENABLED"
            target_capacity     = 100
        }
    }
}

resource "aws_ecs_cluster_capacity_providers" "main" {
    cluster_name = aws_ecs_cluster.cinesense.name
    capacity_providers = [
        aws_ecs_capacity_provider.recommendation.name,
        aws_ecs_capacity_provider.auth.name
    ]
}