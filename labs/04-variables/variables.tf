variable "proyecto" {
  description = "Nombre del proyecto; se usa como prefijo"
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.proyecto))
    error_message = "Solo minúsculas, números y guiones (3-21 caracteres)."
  }
}

variable "entorno" {
  description = "Entorno de despliegue"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.entorno)
    error_message = "entorno debe ser dev, staging o prod."
  }
}

variable "replicas" {
  description = "Número de copias"
  type        = number
  default     = 1

  validation {
    condition     = var.replicas >= 1 && var.replicas <= 5
    error_message = "replicas debe estar entre 1 y 5."
  }
}

variable "habilitar_logs" {
  type    = bool
  default = false
}

variable "etiquetas_extra" {
  type    = map(string)
  default = {}
}
