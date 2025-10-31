data "aws_ami" "ubuntu" {
    most_recent = true

    
}

resource "aws_instance" "backend" {

    instance_market_options {
      market_type = "spot"
      spot_options {
        max_price = 0.0031
      }
    }

    instance_type = "t4g.nano"
    
    tags = {
        ManagedBy = "Terraform"
    }

    #lifecycle {
    #    prevent_destroy = true
    #}
}
