variable "proyecto" {
  type = string
}

variable "entorno" {
  type = string

  validation {
    condition     = contains(["dev", "prod"], var.entorno)
    error_message = "entorno debe ser dev o prod."
  }
}

variable "extra" {
  type    = map(string)
  default = {}
}

output "prefijo" {
  value = "${var.proyecto}-${var.entorno}"
}

output "todas" {
  value = merge(var.extra, {
    Proyecto = var.proyecto
    Entorno  = var.entorno
    Gestion  = "terraform"
  })
}
