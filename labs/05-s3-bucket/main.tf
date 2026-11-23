provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Gestion = "terraform"
      Curso   = "terraform-desde-cero"
    }
  }
}

variable "region" {
  type    = string
  default = "eu-west-1"
}

resource "aws_s3_bucket" "demo" {
  bucket_prefix = "curso-tf-demo-"
  force_destroy = true # solo para labs
}

resource "aws_s3_bucket_versioning" "demo" {
  bucket = aws_s3_bucket.demo.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "demo" {
  bucket = aws_s3_bucket.demo.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "demo" {
  bucket                  = aws_s3_bucket.demo.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "hola" {
  bucket       = aws_s3_bucket.demo.id
  key          = "hola.txt"
  content      = "Subido con Terraform"
  content_type = "text/plain"
}

output "bucket" {
  value = aws_s3_bucket.demo.bucket
}

output "arn" {
  value = aws_s3_bucket.demo.arn
}
