terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  backend "s3" {
    bucket       = "tfstate-123456789012-eu-west-1"
    key          = "proyecto-final/dev/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = "eu-west-1"
  default_tags {
    tags = { Proyecto = "proyecto-final", Entorno = "dev", Gestion = "terraform" }
  }
}

module "network" {
  source   = "../../modules/network"
  nombre   = "pf-dev"
  vpc_cidr = "10.0.0.0/16"
}

module "web" {
  source         = "../../modules/web"
  nombre         = "pf-dev"
  vpc_id         = module.network.vpc_id
  subnet_ids     = module.network.public_subnet_ids
  tipo_instancia = "t3.micro"
  min_instancias = 2
  max_instancias = 2
}

output "url" {
  value = module.web.url
}
