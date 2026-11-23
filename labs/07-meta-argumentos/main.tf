# count: N copias numeradas
resource "local_file" "nota" {
  count    = 3
  filename = "${path.module}/salida/nota-${count.index}.txt"
  content  = "Soy la nota número ${count.index}"
}

# for_each con set: prueba a quitar "luis" y mira el plan
variable "usuarios" {
  type    = set(string)
  default = ["ana", "luis", "marta"]
}

resource "local_file" "perfil" {
  for_each = var.usuarios
  filename = "${path.module}/salida/${each.key}.txt"
  content  = "Perfil de ${each.value}"
}

# for_each con map de objetos
variable "servicios" {
  type = map(object({
    puerto   = number
    replicas = number
  }))
  default = {
    web = { puerto = 80, replicas = 2 }
    api = { puerto = 8080, replicas = 3 }
  }
}

resource "local_file" "servicio" {
  for_each = var.servicios
  filename = "${path.module}/salida/${each.key}.conf"
  content  = "puerto=${each.value.puerto}\nreplicas=${each.value.replicas}\n"
}

# Creación condicional + lifecycle
variable "crear_secreto" {
  type    = bool
  default = true
}

resource "random_password" "secreto" {
  count  = var.crear_secreto ? 1 : 0
  length = 20

  lifecycle {
    prevent_destroy = false # cámbialo a true y prueba terraform destroy
  }
}

output "notas" {
  value = local_file.nota[*].filename
}

output "servicios" {
  value = { for nombre, f in local_file.servicio : nombre => f.filename }
}
