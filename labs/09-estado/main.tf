# Lab de estado sin nube:
# 1. terraform apply
# 2. terraform state list / terraform state show random_pet.mascota
# 3. Edita salida/mascota.txt a mano → terraform plan -refresh-only
# 4. Renombra random_pet.mascota a random_pet.animal y descomenta el bloque moved

resource "random_pet" "mascota" {
  length = 2
}

resource "random_password" "db" {
  length  = 16
  special = true
}

resource "local_file" "mascota" {
  filename = "${path.module}/salida/mascota.txt"
  content  = "Mi mascota se llama ${random_pet.mascota.id}\n"
}

# moved {
#   from = random_pet.mascota
#   to   = random_pet.animal
# }

output "password" {
  value     = random_password.db.result
  sensitive = true # oculto en pantalla, pero en texto plano en terraform.tfstate
}
