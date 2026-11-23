variable "proyecto" {
  description = "Nombre del proyecto. Se usa en los nombres de los recursos"
  type        = string
  default     = "miweb"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,15}$", var.proyecto))
    error_message = "Solo minúsculas, números y guiones (3 a 16 caracteres)."
  }
}

variable "entorno" {
  description = "Entorno: dev o prod"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "prod"], var.entorno)
    error_message = "El entorno debe ser dev o prod."
  }
}

variable "region" {
  description = "Región de AWS"
  type        = string
  default     = "eu-west-1"
}

variable "mi_ip" {
  description = "Tu IP pública en formato CIDR (por ejemplo 81.45.10.20/32). Solo ella podrá entrar por SSH"
  type        = string

  validation {
    condition     = can(cidrhost(var.mi_ip, 0))
    error_message = "mi_ip debe tener formato CIDR, por ejemplo 81.45.10.20/32."
  }
}

variable "ruta_clave_publica" {
  description = "Ruta de tu clave SSH pública"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "servidores" {
  description = "Servidores a crear: nombre => tipo de instancia"
  type        = map(string)
  default = {
    web1 = "t3.micro"
    web2 = "t3.micro"
  }
}
