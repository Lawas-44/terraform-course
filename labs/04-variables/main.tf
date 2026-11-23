locals {
  prefijo = "${var.proyecto}-${var.entorno}"

  etiquetas = merge(
    {
      Proyecto = var.proyecto
      Entorno  = var.entorno
      Gestion  = "terraform"
    },
    var.etiquetas_extra
  )
}

resource "local_file" "config" {
  filename = "${path.module}/${local.prefijo}.json"
  content = jsonencode({
    replicas  = var.replicas
    logs      = var.habilitar_logs
    etiquetas = local.etiquetas
  })
}
