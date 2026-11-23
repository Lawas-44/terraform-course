# Tests del proyecto con AWS simulado: no crean nada ni necesitan credenciales.
mock_provider "aws" {
  mock_data "aws_availability_zones" {
    defaults = {
      names = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
    }
  }

  mock_resource "aws_instance" {
    defaults = {
      public_ip = "203.0.113.10"
    }
  }
}

variables {
  mi_ip              = "81.45.10.20/32"
  ruta_clave_publica = "./tests/clave_de_prueba.pub"
}

run "crea_dos_servidores" {
  command = apply

  assert {
    condition     = length(output.ips) == 2
    error_message = "Deberían crearse 2 servidores"
  }

  assert {
    condition     = contains(keys(output.ips), "web1") && contains(keys(output.ips), "web2")
    error_message = "Los servidores deberían llamarse web1 y web2"
  }

  assert {
    condition     = strcontains(local_file.inventario.content, "web1 ansible_host=203.0.113.10")
    error_message = "El inventario de Ansible no contiene web1"
  }
}

run "rechaza_ip_sin_cidr" {
  command = plan

  variables {
    mi_ip = "81.45.10.20"
  }

  expect_failures = [var.mi_ip]
}
