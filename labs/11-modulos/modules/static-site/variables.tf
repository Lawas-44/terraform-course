variable "nombre" {
  description = "Nombre base del sitio (se usa como prefijo del bucket)"
  type        = string
}

variable "entorno" {
  description = "Entorno: dev o prod"
  type        = string
  default     = "dev"
}

variable "index_html" {
  description = "Contenido HTML de la página principal"
  type        = string
  default     = "<h1>Funciona</h1>"
}

variable "error_html" {
  description = "Contenido de error.html (opcional)"
  type        = string
  default     = null
}

variable "etiquetas" {
  description = "Etiquetas adicionales"
  type        = map(string)
  default     = {}
}
