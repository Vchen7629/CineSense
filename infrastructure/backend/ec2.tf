data "aws_ami" "ecs_optimized" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# recommendations fastapi ec2 server
resource "aws_launch_template" "recommendation" {
    name_prefix   = "ecs-recommendation-"
    image_id      = data.aws_ami.ecs_optimized.id
    instance_type = "t3.medium"

    iam_instance_profile {
      name = aws_iam_instance_profile.ecs_instance_profile.name
    }

    network_interfaces {
        associate_public_ip_address = false
        security_groups             = [aws_security_group.ec2_instances.id]
        delete_on_termination       = true 
    }

    # script that runs when ec2 instance boots to register it with ecs cluster
    user_data = base64encode(<<-EOF
      #!/bin/bash
      echo ECS_CLUSTER=${aws_ecs_cluster.cinesense.name} >> /etc/ecs/ecs.config
      echo ECS_ENABLE_TASK_IAM_ROLE=true >> /etc/ecs/ecs.config
      echo ECS_ENABLE_TASK_IAM_ROLE_NETWORK_HOST=true >> /etc/ecs/ecs.config
    EOF
    )
}

# user auth fastapi ec2 server
resource "aws_launch_template" "auth" {
    name_prefix   = "ecs-auth-"
    image_id      = data.aws_ami.ecs_optimized.id
    instance_type = "t3a.micro"

    iam_instance_profile {
      name = aws_iam_instance_profile.ecs_instance_profile.name
    }

    network_interfaces {
        associate_public_ip_address = false
        security_groups             = [aws_security_group.ec2_instances.id]
        delete_on_termination       = true 
    }

    # script that runs when ec2 instance boots to register it with ecs cluster
    user_data = base64encode(<<-EOF
      #!/bin/bash
      echo ECS_CLUSTER=${aws_ecs_cluster.cinesense.name} >> /etc/ecs/ecs.config
      echo ECS_ENABLE_TASK_IAM_ROLE=true >> /etc/ecs/ecs.config
      echo ECS_ENABLE_TASK_IAM_ROLE_NETWORK_HOST=true >> /etc/ecs/ecs.config
    EOF
    )
}

# auto scaling group for ec2, added this for auto replacement if instance fails
resource "aws_autoscaling_group" "ecs_asg_recommendations" {
  name                 = "cinesense-recommendation-asg" 
  desired_capacity     = 1
  min_size             = 1
  max_size             = 1

  launch_template {
    id      = aws_launch_template.recommendation.id
    version = "$Latest"
  }

  vpc_zone_identifier  = [aws_subnet.private.id]
}

resource "aws_autoscaling_group" "ecs_asg_auth" {
  name                 = "cinesense-auth-asg"
  desired_capacity     = 1
  min_size             = 1
  max_size             = 1

  launch_template {
    id      = aws_launch_template.auth.id
    version = "$Latest"
  }

  vpc_zone_identifier = [aws_subnet.private.id]
}