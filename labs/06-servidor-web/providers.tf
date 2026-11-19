provider "aws" {
  region = var.region

  default_tags {
    tags = { Gestion = "terraform", Curso = "modulo-06" }
  }
}

variable "region" {
  type    = string
  default = "eu-west-1"
}
