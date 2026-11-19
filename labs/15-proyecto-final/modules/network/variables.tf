variable "nombre" {
  type = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr debe ser un CIDR válido."
  }
}

variable "num_zonas" {
  type    = number
  default = 2
  validation {
    condition     = var.num_zonas >= 2 && var.num_zonas <= 3
    error_message = "Entre 2 y 3 zonas (el ALB necesita al menos 2)."
  }
}

output "vpc_id" {
  value = aws_vpc.this.id
}

output "public_subnet_ids" {
  value = [for s in aws_subnet.publica : s.id]
}
