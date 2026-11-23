terraform {
  required_version = ">= 1.10"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }

  # Configuración parcial: terraform init -backend-config=dev.s3.tfbackend
  backend "s3" {}
}
