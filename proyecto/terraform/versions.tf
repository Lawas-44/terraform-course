terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }

  # Estado remoto (paso 10). Se configura con:
  #   terraform init -backend-config=backend.hcl
  backend "s3" {}
}
