resource "aws_secretsmanager_secret" "db_credentials" {
    name                    = "cinesense/db/credentials_v2"
    description             = "Database credentials for CineSense"
    recovery_window_in_days = 0

    tags = {
        Name = "cinesense-db-credentials"
    }
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
    secret_id = aws_secretsmanager_secret.db_credentials.id

    secret_string = jsonencode({
        username = var.db_username
        password = var.db_password
        host     = aws_db_instance.postgres.address
        port     = aws_db_instance.postgres.port
        dbname   = "cinesense_db"
        engine   = "postgres"
    })
}

