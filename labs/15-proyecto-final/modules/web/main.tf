data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# --- Security groups ---
resource "aws_security_group" "alb" {
  name_prefix = "${var.nombre}-alb-"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  # trivy:ignore:AVD-AWS-0107 El balanceador es público por diseño
  security_group_id = aws_security_group.alb.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "alb_a_app" {
  security_group_id            = aws_security_group.alb.id
  referenced_security_group_id = aws_security_group.app.id
  from_port                    = 80
  to_port                      = 80
  ip_protocol                  = "tcp"
}

resource "aws_security_group" "app" {
  name_prefix = "${var.nombre}-app-"
  vpc_id      = var.vpc_id
}

# Las instancias SOLO aceptan tráfico del balanceador
resource "aws_vpc_security_group_ingress_rule" "app_desde_alb" {
  security_group_id            = aws_security_group.app.id
  referenced_security_group_id = aws_security_group.alb.id
  from_port                    = 80
  to_port                      = 80
  ip_protocol                  = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "app_salida" {
  security_group_id = aws_security_group.app.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# --- Balanceador ---
resource "aws_lb" "this" {
  name_prefix        = "web-"
  load_balancer_type = "application"
  subnets            = var.subnet_ids
  security_groups    = [aws_security_group.alb.id]
}

resource "aws_lb_target_group" "this" {
  name_prefix = "web-"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id

  health_check {
    path    = "/"
    matcher = "200"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

# --- Servidores ---
resource "aws_launch_template" "this" {
  name_prefix            = "${var.nombre}-"
  image_id               = data.aws_ami.al2023.id
  instance_type          = var.tipo_instancia
  vpc_security_group_ids = [aws_security_group.app.id]

  metadata_options {
    http_tokens = "required"
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    dnf install -y nginx
    TOKEN=$(curl -s -X PUT http://169.254.169.254/latest/api/token \
      -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
    ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
      http://169.254.169.254/latest/meta-data/instance-id)
    echo "<h1>${var.nombre}</h1><p>Servido por $ID</p>" > /usr/share/nginx/html/index.html
    systemctl enable --now nginx
  EOF
  )
}

resource "aws_autoscaling_group" "this" {
  name_prefix         = "${var.nombre}-"
  min_size            = var.min_instancias
  max_size            = var.max_instancias
  desired_capacity    = var.min_instancias
  vpc_zone_identifier = var.subnet_ids
  target_group_arns   = [aws_lb_target_group.this.arn]
  health_check_type   = "ELB"

  launch_template {
    id      = aws_launch_template.this.id
    version = "$Latest"
  }

  instance_refresh {
    strategy = "Rolling"
  }

  tag {
    key                 = "Name"
    value               = var.nombre
    propagate_at_launch = true
  }
}
