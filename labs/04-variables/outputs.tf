output "archivo_config" {
  description = "Ruta del archivo de configuración generado"
  value       = local_file.config.filename
}

output "resumen" {
  value = {
    proyecto = var.proyecto
    entorno  = var.entorno
    replicas = var.replicas
  }
}
