variable "s3-bucket-name" {
  description   = "s3 bucket name"
  type          = string
  default       = "movie-recommendation-frontend"
}

variable "aws-access-key" {
    description = "iam user access key"
    type        = string
    sensitive   = true
}

variable "aws-secret-access-key" {
    description = "iam user secret access key"
    type        = string
    sensitive   = true
}