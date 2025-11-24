resource "aws_vpc" "main" {
    cidr_block              = "10.0.0.0/16"
    enable_dns_hostnames    = true
    enable_dns_support      = true

    tags = {
        Name = "cinesense-vpc"
    }
}


resource "aws_subnet" "public" {
    vpc_id              = aws_vpc.main.id
    cidr_block          = "10.0.1.0/24"
    availability_zone   = "us-west-1a"
    map_public_ip_on_launch = true

    tags = {
        Name = "cinesense-public-subnet-1"
    }
}

resource "aws_subnet" "public_2" {
    vpc_id              = aws_vpc.main.id
    cidr_block          = "10.0.2.0/24"
    availability_zone   = "us-west-1c"
    map_public_ip_on_launch = true

    tags = {
        Name = "cinesense-public-subnet-2"
    }
}

resource "aws_subnet" "private" {
    vpc_id              = aws_vpc.main.id
    cidr_block          = "10.0.3.0/24"
    availability_zone   = "us-west-1a"

    tags = {
        Name = "cinesense-private-subnet"
    }
}

resource "aws_subnet" "private_2" {
    vpc_id              = aws_vpc.main.id
    cidr_block          = "10.0.4.0/24"
    availability_zone   = "us-west-1c"

    tags = {
        Name = "cinesense-private-subnet-2"
    }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "cinesense-igw"
  }
}

resource "aws_route_table" "private" {
    vpc_id = aws_vpc.main.id

    tags = {
        Name = "cinesense-private-rt"
    }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "cinesense-public-rt"
  }
}

resource "aws_route_table_association" "public" {
    subnet_id      = aws_subnet.public.id
    route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
    subnet_id      = aws_subnet.public_2.id
    route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private_1" {
    subnet_id       = aws_subnet.private.id
    route_table_id  = aws_route_table.private.id
}

resource "aws_route_table_association" "private_2" {
    subnet_id       = aws_subnet.private_2.id
    route_table_id  = aws_route_table.private.id
}

# vpc endpoint so ecs fastapi container can download model files
resource "aws_vpc_endpoint" "s3" {
    vpc_id              = aws_vpc.main.id
    service_name        = "com.amazonaws.us-west-1.s3"
    vpc_endpoint_type   = "Gateway"
    route_table_ids     = [aws_route_table.private.id]

    tags = {
        Name = "cinesense-s3-endpoint"
    }
}

# vpc endpoint for ecr api endpoint for docker image metadata
resource "aws_vpc_endpoint" "ecr_api" {
    vpc_id              = aws_vpc.main.id
    service_name        = "com.amazonaws.us-west-1.ecr.api"
    vpc_endpoint_type   = "Interface"
    subnet_ids          = [aws_subnet.private.id, aws_subnet.private_2.id]
    security_group_ids  = [aws_security_group.vpc_endpoints.id] 
    private_dns_enabled = true

    tags = {
        Name = "cinesense-ecr-api-endpoint"
    }
}

# vpc endpoint for ecr dkr endpoint
resource "aws_vpc_endpoint" "ecr_dkr" {
    vpc_id              = aws_vpc.main.id
    service_name        = "com.amazonaws.us-west-1.ecr.dkr"
    vpc_endpoint_type   = "Interface"
    subnet_ids          = [aws_subnet.private.id, aws_subnet.private_2.id]
    security_group_ids  = [aws_security_group.vpc_endpoints.id] 
    private_dns_enabled = true

    tags = {
        Name = "cinesense-ecr-dkr-endpoint"
    }
}

# vpc endpoint for ecs endpoint
resource "aws_vpc_endpoint" "ecs" {
    vpc_id              = aws_vpc.main.id
    service_name        = "com.amazonaws.us-west-1.ecs"
    vpc_endpoint_type   = "Interface"
    subnet_ids          = [aws_subnet.private.id, aws_subnet.private_2.id]
    security_group_ids  = [aws_security_group.vpc_endpoints.id] 
    private_dns_enabled = true

    tags = {
        Name = "cinesense-ecs-endpoint"
    }
}

# vpc endpoint for ecs agent endpoint
resource "aws_vpc_endpoint" "ecs_agent" {
    vpc_id              = aws_vpc.main.id
    service_name        = "com.amazonaws.us-west-1.ecs-agent"
    vpc_endpoint_type   = "Interface"
    subnet_ids          = [aws_subnet.private.id, aws_subnet.private_2.id]
    security_group_ids  = [aws_security_group.vpc_endpoints.id] 
    private_dns_enabled = true

    tags = {
        Name = "cinesense-ecs-agent-endpoint"
    }
}

# vpc endpoint for ecs telemetry endpoint
resource "aws_vpc_endpoint" "ecs_telemetry" {
    vpc_id              = aws_vpc.main.id
    service_name        = "com.amazonaws.us-west-1.ecs-telemetry"
    vpc_endpoint_type   = "Interface"
    subnet_ids          = [aws_subnet.private.id, aws_subnet.private_2.id]
    security_group_ids  = [aws_security_group.vpc_endpoints.id] 
    private_dns_enabled = true

    tags = {
        Name = "cinesense-ecs-telemetry-endpoint"
    }
}

# vpc endpoint for cloudwatch logs endpoint
resource "aws_vpc_endpoint" "logs" {
    vpc_id              = aws_vpc.main.id
    service_name        = "com.amazonaws.us-west-1.logs"
    vpc_endpoint_type   = "Interface"
    subnet_ids          = [aws_subnet.private.id, aws_subnet.private_2.id]
    security_group_ids  = [aws_security_group.vpc_endpoints.id] 
    private_dns_enabled = true

    tags = {
        Name = "cinesense-logs-endpoint"
    }
}

# vpc endpoint for secrets manager endpoint
resource "aws_vpc_endpoint" "secretsmanager" {
    vpc_id              = aws_vpc.main.id
    service_name        = "com.amazonaws.us-west-1.secretsmanager"
    vpc_endpoint_type   = "Interface"
    subnet_ids          = [aws_subnet.private.id, aws_subnet.private_2.id]
    security_group_ids  = [aws_security_group.vpc_endpoints.id] 
    private_dns_enabled = true

    tags = {
        Name = "cinesense-secretsmanager-endpoint"
    }
}