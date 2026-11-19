output "ips" {
  description = "IP pública de cada servidor"
  value       = module.servidores.ips
}

output "urls" {
  description = "Dirección web de cada servidor"
  value       = { for nombre, ip in module.servidores.ips : nombre => "http://${ip}" }
}

output "ssh" {
  description = "Comando para entrar en cada servidor"
  value       = { for nombre, ip in module.servidores.ips : nombre => "ssh ubuntu@${ip}" }
}
