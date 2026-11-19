data "aws_vpc" "default" {
  default = true
}

resource "aws_s3_bucket" "legado" {
  bucket = "legado-123456789012"
}

resource "aws_security_group" "legado" {
  name        = "legado-sg"
  description = "Creado a mano"
  vpc_id      = data.aws_vpc.default.id
}
