variable "nombre" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }

variable "tipo_instancia" {
  type    = string
  default = "t3.micro"
}

variable "min_instancias" {
  type    = number
  default = 2
}

variable "max_instancias" {
  type    = number
  default = 4
  validation {
    condition     = var.max_instancias <= 6
    error_message = "Máximo 6 instancias para controlar el coste."
  }
}

output "url" {
  value = "http://${aws_lb.this.dns_name}"
}
