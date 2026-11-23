variable "nombre" {
  description = "Prefijo para los nombres"
  type        = string
}

variable "servidores" {
  description = "Servidores a crear: nombre => tipo de instancia"
  type        = map(string)
}

variable "vpc_id" {
  type = string
}

variable "subnet_id" {
  type = string
}

variable "clave_ssh" {
  description = "Nombre del par de claves de AWS"
  type        = string
}

variable "mi_ip" {
  description = "IP (CIDR) desde la que se permite SSH"
  type        = string
}
