output "nombre_bucket" {
  description = "Nombre del bucket creado"
  value       = aws_s3_bucket.this.bucket
}

output "url" {
  description = "URL pública de la web"
  value       = "http://${aws_s3_bucket_website_configuration.this.website_endpoint}"
}
