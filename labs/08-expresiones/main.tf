# Abre `terraform console` en esta carpeta y evalúa cada local.

variable "entorno" {
  type    = string
  default = "dev"
}

variable "etiquetas" {
  type = map(string)
  default = {
    "Centro Coste" = "1234"
    "OWNER"        = "Ana"
  }
}

locals {
  nombres    = ["ana", "luis", "marta"]
  mayusculas = [for n in local.nombres : upper(n)]
  largos     = [for n in local.nombres : n if length(n) > 3]
  numerados  = [for i, n in local.nombres : "${i + 1}. ${n}"]
  longitudes = { for n in local.nombres : n => length(n) }

  precios    = { cafe = 1.5, te = 1.2, zumo = 3 }
  solo_caros = { for k, v in local.precios : k => v if v > 2 }

  es_prod        = var.entorno == "prod"
  tipo_instancia = local.es_prod ? "t3.medium" : "t3.micro"

  vpc_cidr = "10.20.0.0/16"
  red = {
    for i, z in ["a", "b", "c"] : z => {
      publica = cidrsubnet(local.vpc_cidr, 8, i)
      privada = cidrsubnet(local.vpc_cidr, 8, i + 100)
    }
  }

  etiquetas_normalizadas = merge(
    { for k, v in var.etiquetas : replace(lower(k), " ", "-") => v },
    { gestion = "terraform" }
  )

  politica = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = ["arn:aws:s3:::mi-bucket/*"]
    }]
  })
}

resource "local_file" "user_data" {
  filename = "${path.module}/user_data.sh"
  content = templatefile("${path.module}/templates/user_data.sh.tftpl", {
    titulo    = "Entorno ${var.entorno}"
    servicios = ["web", "api", "worker"]
  })
}

output "red" {
  value = local.red
}

output "etiquetas" {
  value = local.etiquetas_normalizadas
}
