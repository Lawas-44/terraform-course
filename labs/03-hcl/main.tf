locals {
  texto  = "hola"
  numero = 42
  activo = true
  lista  = ["a", "b", "c"]
  mapa   = { entorno = "dev", equipo = "plataforma" }
  objeto = { nombre = "web", puertos = [80, 443] }

  app = {
    nombre     = "tienda"
    version    = 3
    servidores = ["web1", "web2", "api1"]
  }
}

resource "random_integer" "puerto" {
  min = 8000
  max = 8999
}

resource "local_file" "env" {
  filename = "${path.module}/.env"
  content  = "PORT=${random_integer.puerto.result}\n"
}

resource "local_file" "inventario" {
  filename = "${path.module}/inventario.txt"
  content  = <<-EOT
    # ${local.app.nombre} v${local.app.version}
    %{for s in local.app.servidores~}
    ${s}
    %{endfor~}
  EOT
}

output "puerto" {
  value = random_integer.puerto.result
}
