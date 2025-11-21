resource "aws_" "frontend" {
    bucket ="movie-recommendation-frontend-${random_id.suffix.hex}"

    tags = {
        ManagedBy = "Terraform"
    }

    #lifecycle {
    #    prevent_destroy = true
    #}
}
