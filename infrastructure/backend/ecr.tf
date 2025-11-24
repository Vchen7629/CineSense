# for recommendation fastapi docker image
resource "aws_ecr_repository" "recommendation_repo" {
    name                    = "recommendation-repo"
    image_tag_mutability    = "MUTABLE"

    image_scanning_configuration {
        scan_on_push        = true
    }

    tags = {
        Name                = "cinesense-recommendation-repo"
    }
}

# for user auth fastapi docker image
resource "aws_ecr_repository" "auth_repo" {
    name                    = "auth-repo"
    image_tag_mutability    = "MUTABLE"

    image_scanning_configuration {
        scan_on_push        = true
    }

    tags = {
        Name                = "cinesense-auth-repo"
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