mock_provider "aws" {
  mock_data "aws_availability_zones" {
    defaults = {
      names = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
    }
  }
}

variables {
  nombre    = "test"
  num_zonas = 3
}

run "tres_subredes" {
  command = apply

  assert {
    condition     = length(aws_subnet.publica) == 3
    error_message = "Deberían crearse 3 subredes"
  }

  assert {
    condition     = aws_subnet.publica["eu-west-1a"].cidr_block == "10.0.0.0/24"
    error_message = "CIDR inesperado en la primera subred"
  }
}
