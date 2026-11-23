terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

module "tags" {
  source   = "./modules/etiquetas"
  proyecto = "curso"
  entorno  = "dev"
}

variable "sitios" {
  type = map(string)
  default = {
    dev  = "<h1>Entorno de desarrollo</h1>"
    prod = "<h1>Producción</h1>"
  }
}

module "web" {
  source   = "./modules/static-site"
  for_each = var.sitios

  nombre     = "curso"
  entorno    = each.key
  index_html = each.value
  etiquetas  = module.tags.todas
}

output "urls" {
  value = { for k, m in module.web : k => m.url }
}
