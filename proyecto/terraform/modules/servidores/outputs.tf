output "ips" {
  description = "IP pública de cada servidor"
  value       = { for nombre, servidor in aws_instance.this : nombre => servidor.public_ip }
}
