resource "aws_lb" "main" {
    name                        = "cinesense-alb"
    internal                    = false
    load_balancer_type          = "application"
    security_groups             = [aws_security_group.alb.id]
    subnets                     = [aws_subnet.public.id, aws_subnet.public_2.id]

    enable_deletion_protection  = false

    tags = {
        Name                    = "cinesense-alb"
    }
}

resource "aws_lb_target_group" "recommendation" {
    name                        = "cinesense-recommendation-tg"
    port                        = 8000
    protocol                    = "HTTP"
    vpc_id                      = aws_vpc.main.id
    target_type                 = "ip"

    health_check {
        path                    = "/health"
        healthy_threshold       = 2
        unhealthy_threshold     = 10
        timeout                 = 10
        interval                = 30
        matcher                 = "200"
    } 

    tags = {
        Name = "cinesense-recommendation-tg"
    }
}

resource "aws_lb_target_group" "auth" {
    name                        = "cinesense-auth-tg"
    port                        = 8000
    protocol                    = "HTTP"
    vpc_id                      = aws_vpc.main.id
    target_type                 = "ip"

    health_check {
        path                    = "/health"
        healthy_threshold       = 2
        unhealthy_threshold     = 3
        timeout                 = 5
        interval                = 30
        matcher                 = "200" 
    } 

    tags = {
        Name = "cinesense-auth-tg"
    }
}

resource "aws_lb_listener" "http" {
    load_balancer_arn           = aws_lb.main.id
    port                        = "80"
    protocol                    = "HTTP"

    default_action {
        type                    = "forward"
        target_group_arn        = aws_lb_target_group.recommendation.arn 
    } 
}

resource "aws_lb_listener_rule" "recommendation" {
    listener_arn                = aws_lb_listener.http.arn
    priority                    = 100

    action {
        type                    = "forward"
        target_group_arn        = aws_lb_target_group.recommendation.arn
    }

    condition {
        path_pattern {
            values = ["/api/recommendations/*"]
        }
    } 
}

resource "aws_lb_listener_rule" "auth" {
    listener_arn                = aws_lb_listener.http.arn
    priority                    = 200

    action {
        type                    = "forward"
        target_group_arn        = aws_lb_target_group.auth.arn
    }

    condition {
        path_pattern {
            values = ["/api/auth/*"]
        }
    } 
}