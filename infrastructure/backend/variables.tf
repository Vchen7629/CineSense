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
