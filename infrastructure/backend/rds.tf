
resource "aws_db_instance" "postgres" {
    allocated_storage       = 20
    db_name                 = "cinesense_db"
    instance_class          = "db.t4g.medium"
    engine                  = "postgres"
    engine_version          = "17"

    multi_az                = false
    availability_zone       = "us-west-1a"
    
    publicly_accessible     = false
    username                = var.db_username
    password                = var.db_password
    
    storage_type            = "gp2"
    backup_retention_period = 7
    deletion_protection     = true

    db_subnet_group_name    = aws_db_subnet_group.main.name 
    vpc_security_group_ids  = [aws_security_group.rds.id]

    skip_final_snapshot     = false
    final_snapshot_identifier = "cinesense-db-final-snapshot"

    tags = {
      Name = "cinesense-postgres"
    }
}

# Single AZ deployment still requires 2 subnets
resource "aws_db_subnet_group" "main" {
    name = "cinesense-db-subnet-group"
    subnet_ids = [
        aws_subnet.private.id,
        aws_subnet.private_2.id
    ]

    tags = {
        Name = "cinesense-db-subnet-group"
    }
}

# Note: pgvector is available as a standard extension in RDS Postgres 17
# No parameter group needed - just use CREATE EXTENSION vector;