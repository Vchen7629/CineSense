# for recommendation fastapi docker image
resource "aws_ecr_repository" "recommendation_api" {
    name                    = "cinesense-recommendation-api"
    image_tag_mutability    = "MUTABLE"

    image_scanning_configuration {
        scan_on_push        = true
    }

    tags = {
        Name                = "cinesense-recommendation-api"
    }
}

# for user auth fastapi docker image
resource "aws_ecr_repository" "auth_api" {
    name                    = "cinesense-auth-api"
    image_tag_mutability    = "MUTABLE"

    image_scanning_configuration {
        scan_on_push        = true
    }

    tags = {
        Name                = "cinesense-auth-api"
    }
}

# for alembic docker image to manage migrations
resource "aws_ecr_repository" "migration_repo" {
    name                    = "cinesense-migration"
    image_tag_mutability    = "MUTABLE"

    image_scanning_configuration {
        scan_on_push        = true
    }

    tags = {
        Name                = "cinesense-migration-repo"
    }
}