# Get git commit SHA for image tagging
data "external" "git_sha" {
    program = ["sh", "-c", "echo '{\"sha\":\"'$(git rev-parse HEAD)'\"}'"]
    working_dir = path.module
}

locals {
    git_sha_short = substr(data.external.git_sha.result.sha, 0, 8)
}

# build and push migration dockerfile
resource "null_resource" "migration_image" {
    triggers = {
        dockerfile_hash = filemd5("${path.module}/../../backend/database/Dockerfile")
        handler_hash    = filemd5("${path.module}/../../backend/database/lambda_handler.py")
        git_sha         = local.git_sha_short
    }

    provisioner "local-exec" {
        command = <<-EOT
            set -e
            echo "Building migration image with tag: ${local.git_sha_short}"

            # login to ECR
            aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin ${aws_ecr_repository.migration_repo.repository_url}

            # Build and push migration image for Lambda (x86_64 architecture)
            cd ${path.module}/../../backend/database
            docker build --platform linux/amd64 --provenance=false -t ${aws_ecr_repository.migration_repo.repository_url}:${local.git_sha_short} .
            docker push ${aws_ecr_repository.migration_repo.repository_url}:${local.git_sha_short}
        EOT

        environment = {
            AWS_CONFIG_FILE       = "$HOME/.aws/config"
            AWS_SHARED_CREDENTIALS_FILE = "$HOME/.aws/credentials"
            AWS_PROFILE           = "default"
        }
    }

    depends_on = [aws_ecr_repository.migration_repo]
}

# Lambda Function for database migrations
resource "aws_lambda_function" "db_migration" {
    function_name           = "cinesense-db-migration"
    role                    = aws_iam_role.lambda_migration_role.arn

    package_type            = "Image"
    image_uri               = "${aws_ecr_repository.migration_repo.repository_url}:${local.git_sha_short}"
    depends_on              = [null_resource.migration_image]

    timeout                 = 300
    memory_size             = 512

    vpc_config {
      subnet_ids            = [aws_subnet.private.id, aws_subnet.private_2.id]
      security_group_ids    = [aws_security_group.lambda_migration.id]
    } 

    environment {
        variables = {
            SECRET_ARN = aws_secretsmanager_secret.db_credentials.arn
        }
    }

    tags = {
        Name                = "cinesense-db-migration"
    }
}

# Auto-invoke Lambda to run migrations after creation/updates
resource "null_resource" "run_migrations" {
    triggers = {
        # Run migrations when Lambda or database changes
        lambda_version = aws_lambda_function.db_migration.version
        db_address     = aws_db_instance.postgres.address
    }

    provisioner "local-exec" {
        command = <<-EOT
            echo "Running database migrations..."
            aws lambda invoke \
              --function-name ${aws_lambda_function.db_migration.function_name} \
              --region us-west-1 \
              --log-type Tail \
              /tmp/migration-response.json

            echo "Migration output:"
            cat /tmp/migration-response.json

            # Check for errors
            if grep -q "errorMessage" /tmp/migration-response.json; then
                echo "Migration failed!"
                exit 1
            fi

            echo "Migrations completed successfully"
        EOT
    }

    depends_on = [aws_lambda_function.db_migration, aws_db_instance.postgres]
}
