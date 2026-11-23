locals {
  prefijo = "${var.proyecto}-${var.entorno}"

  etiquetas = {
    Proyecto = var.proyecto
    Entorno  = var.entorno
    Gestion  = "terraform"
  }
}
