
resource "aws_db_instance" "postgres" {
    allocated_storage = 20
    db_name = "cinesense_db"
    instance_class = "db.t4g.medium"
    engine = "postgres"
    engine_version = "17"
    publicly_accessible = false
    
    storage_type = "gp2"
    backup_retention_period = 0
    deletion_protection  = false
}