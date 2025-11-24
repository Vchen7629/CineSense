variable "aws-model-file-s3-name" {
    description = "bucket name for hosting versioned recommendation model files"
    type        = string
    default     = "cinesense-ml-artifacts-prod"
}

variable "db_username" {
    description = "postgres database username"
    type        = string
    sensitive   = true
}

variable "db_password" {
    description = "postgres database password"
    type        = string
    sensitive   = true
}

variable "cloudflare_api_token" {
    description = "Cloudflare API token"
    type        = string
    sensitive   = true
}

variable "cloudflare_zone_id" {
    description = "Cloudflare zone ID for cinesense.tech"
    type        = string
}