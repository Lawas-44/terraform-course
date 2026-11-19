terraform {
  required_version = ">= 1.6"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

resource "random_pet" "nombre" {
  length = 2
}

resource "local_file" "saludo" {
  filename = "${path.module}/saludo.txt"
  content  = "¡Hola, ${random_pet.nombre.id}! Este archivo lo creó Terraform.\n"
}

output "nombre_mascota" {
  value = random_pet.nombre.id
}
