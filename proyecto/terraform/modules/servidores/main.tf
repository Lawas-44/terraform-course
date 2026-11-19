# Imagen más reciente de Ubuntu 24.04
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical, la empresa de Ubuntu

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }
}

# Firewall de los servidores
resource "aws_security_group" "web" {
  name_prefix = "${var.nombre}-web-"
  description = "SSH desde mi IP y HTTP desde Internet"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = var.mi_ip
  from_port         = 22
  to_port           = 22
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  # trivy:ignore:AVD-AWS-0107 Web pública: debe aceptar HTTP desde Internet
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "todo" {
  # trivy:ignore:AVD-AWS-0104 Los servidores necesitan descargar paquetes
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# Un servidor por cada elemento de var.servidores
resource "aws_instance" "this" {
  for_each = var.servidores

  ami                    = data.aws_ami.ubuntu.id
  instance_type          = each.value
  subnet_id              = var.subnet_id
  key_name               = var.clave_ssh
  vpc_security_group_ids = [aws_security_group.web.id]

  metadata_options {
    http_tokens = "required"
  }

  root_block_device {
    encrypted = true
  }

  tags = {
    Name = "${var.nombre}-${each.key}"
    Rol  = "web"
  }
}
