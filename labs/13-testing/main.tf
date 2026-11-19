variable "proyecto" {
  type = string

  validation {
    condition     = length(var.proyecto) >= 3
    error_message = "proyecto debe tener al menos 3 caracteres."
  }
}

variable "entorno" {
  type    = string
  default = "dev"
}

locals {
  prefijo = "${var.proyecto}-${var.entorno}"
}

resource "local_file" "config" {
  filename = "${path.module}/${local.prefijo}.conf"
  content  = "proyecto=${var.proyecto}\nentorno=${var.entorno}\n"

  lifecycle {
    postcondition {
      condition     = endswith(self.filename, ".conf")
      error_message = "El archivo debe tener extensión .conf"
    }
  }
}

output "prefijo" {
  value = local.prefijo
}
