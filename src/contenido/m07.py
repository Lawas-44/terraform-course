# -*- coding: utf-8 -*-
# Módulo 07 · Meta-argumentos

LECCION = [
 ("h", "Qué son los meta-argumentos"),
 ("p", "Son opciones especiales que puedes poner en **cualquier** recurso para cambiar cómo lo trata Terraform:"),
 ("table", ["Opción", "Para qué sirve"], [
  ["`count`", "Crear varias copias numeradas"],
  ["`for_each`", "Crear una copia por cada elemento de una lista de nombres"],
  ["`lifecycle`", "Proteger un recurso o cambiar cómo se reemplaza"],
  ["`depends_on`", "Indicar un orden a mano (módulo 6)"],
  ["`provider`", "Elegir otra región o cuenta (módulo 5)"],
 ]),
 ("p", "En los ejemplos usamos archivos locales para practicar gratis. Con recursos de AWS funciona igual."),

 ("h", "count: varias copias"),
 ("code", "hcl", "count.tf", """resource "local_file" "nota" {
  count    = 3
  filename = "nota-${count.index}.txt"
  content  = "Soy la nota ${count.index}"
}"""),
 ("p", "Crea `nota-0.txt`, `nota-1.txt` y `nota-2.txt`. `count.index` es el número de cada copia, empezando por 0."),
 ("p", "Un uso muy común: crear algo **solo si** se cumple una condición. Con 1 se crea y con 0 no:"),
 ("code", "hcl", "crear solo si...", """variable "crear_backup" {
  type    = bool
  default = false
}

resource "aws_s3_bucket" "backup" {
  count         = var.crear_backup ? 1 : 0
  bucket_prefix = "backup-"
}"""),

 ("h", "for_each: copias con nombre"),
 ("p", "`for_each` crea una copia por cada elemento, y cada copia se identifica **por su nombre**, no por un número:"),
 ("code", "hcl", "for_each.tf", """variable "usuarios" {
  type    = set(string)
  default = ["ana", "luis", "marta"]
}

resource "local_file" "perfil" {
  for_each = var.usuarios
  filename = "${each.key}.txt"
  content  = "Perfil de ${each.key}"
}"""),
 ("p", "Dentro del bloque, `each.key` es el elemento actual: \"ana\", \"luis\" o \"marta\"."),
 ("p", "También puedes usar un mapa para dar datos distintos a cada copia. Entonces `each.key` es el nombre y `each.value` su valor:"),
 ("code", "hcl", "for_each con mapa", """resource "local_file" "servicio" {
  for_each = {
    web = 80
    api = 8080
  }
  filename = "${each.key}.conf"
  content  = "puerto=${each.value}"
}"""),

 ("h", "Por qué for_each suele ser mejor"),
 ("p", "Imagina que creas los perfiles con `count` sobre la lista `[\"ana\", \"luis\", \"marta\"]` y luego quitas a luis. Con `count` las copias se identifican por posición: marta pasa de la posición 2 a la 1, y Terraform cree que ha cambiado:"),
 ("term", """$ terraform plan
  # local_file.perfil[1] must be replaced
  # local_file.perfil[2] will be destroyed

Plan: 1 to add, 0 to change, 2 to destroy."""),
 ("p", "Con `for_each` solo se borra lo que has quitado:"),
 ("term", """$ terraform plan
  # local_file.perfil["luis"] will be destroyed

Plan: 0 to add, 0 to change, 1 to destroy."""),
 ("tip", "Regla sencilla: usa `count` para «N copias iguales» o «crear sí/no», y `for_each` para listas de cosas con nombre."),

 ("h", "lifecycle: proteger y controlar"),
 ("code", "hcl", "lifecycle", """resource "aws_s3_bucket" "datos" {
  bucket_prefix = "datos-"

  lifecycle {
    prevent_destroy = true            # impide borrarlo
    ignore_changes  = [tags]          # no deshacer cambios de etiquetas hechos a mano
  }
}"""),
 ("table", ["Opción", "Qué hace"], [
  ["`prevent_destroy`", "Da error si algo intenta borrar el recurso. Ideal para bases de datos"],
  ["`ignore_changes`", "Terraform no toca esos datos aunque alguien los cambie fuera"],
  ["`create_before_destroy`", "Al reemplazar, crea el nuevo antes de borrar el viejo"],
 ]),
 ("term", """$ terraform destroy
Error: Instance cannot be destroyed

Resource aws_s3_bucket.datos has lifecycle.prevent_destroy set"""),
 ("p", "Para poder borrarlo, primero tienes que quitar `prevent_destroy` del código."),

 ("h", "Forzar que se cree de nuevo"),
 ("p", "Si un recurso funciona mal y quieres que Terraform lo cree otra vez:"),
 ("term", """$ terraform apply -replace="aws_instance.web\""""),
 ("info", "En tutoriales antiguos verás `terraform taint`. Hace lo mismo, pero ya no se usa."),
]

TEST = [
 ("¿Qué valor tiene `count.index` en la tercera copia de un recurso?",
  ["3", "2", "1", "c"], 1, "Los índices empiezan en 0: 0, 1, 2."),
 ("¿Cómo creas un recurso solo si `var.activar` es true?",
  ["if var.activar { ... }", "count = var.activar ? 1 : 0", "enabled = var.activar", "for_each = var.activar"], 1,
  "Es el patrón clásico: 1 copia o ninguna."),
 ("Usas `count` sobre una lista de 5 nombres y eliminas el segundo. ¿Qué pasa?",
  ["Solo se borra el segundo", "Se recrean/desplazan los recursos posteriores", "Nada", "Error"], 1,
  "Los índices se desplazan y Terraform cree que los recursos 1-3 han cambiado."),
 ("Con `for_each = { web = 80, api = 8080 }`, ¿qué vale `each.value` en la copia \"api\"?",
  ["\"api\"", "8080", "1", "{api = 8080}"], 1, "`each.key` es la clave (\"api\") y `each.value` su valor (8080)."),
 ("¿Qué opción de lifecycle evita borrar un recurso por accidente?",
  ["ignore_changes", "create_before_destroy", "prevent_destroy", "replace_triggered_by"], 2,
  "Hace que cualquier plan que implique destruirlo falle."),
 ("Un equipo modifica las etiquetas de una instancia desde la consola y no quieres que Terraform las revierta. ¿Qué usas?",
  ["prevent_destroy", "ignore_changes = [tags]", "depends_on", "-replace"], 1,
  "`ignore_changes` hace que Terraform no proponga cambios en esos atributos."),
 ("¿Cuál es la alternativa moderna a `terraform taint`?",
  ["terraform destroy -target", "terraform apply -replace=DIRECCION", "terraform state rm", "terraform refresh"], 1,
  "`-replace` fuerza la recreación y muestra el plan antes."),
]

RETOS = [
 {"titulo": "Equipo con permisos",
  "enunciado": "Crea una variable `equipo` de tipo `map(string)` que asocie nombre → rol (`ana = \"admin\"`, `luis = \"dev\"`, `marta = \"dev\"`). Genera un archivo por persona con su rol. Después quita a `luis` y comprueba que el plan solo destruye su archivo.",
  "pista": "`for_each = var.equipo`, `each.key` es el nombre y `each.value` el rol.",
  "solucion": ("hcl", """variable "equipo" {
  type = map(string)
  default = {
    ana   = "admin"
    luis  = "dev"
    marta = "dev"
  }
}

resource "local_file" "miembro" {
  for_each = var.equipo
  filename = "${path.module}/equipo/${each.key}.txt"
  content  = "${each.key} tiene el rol ${each.value}\\n"
}""")},
 {"titulo": "Migrar de count a for_each",
  "enunciado": "Tienes `local_file.perfil` creado con `count` sobre `[\"ana\", \"luis\"]`. Cámbialo a `for_each` sin que Terraform recree los archivos.",
  "pista": "Necesitas decirle a Terraform que `perfil[0]` ahora se llama `perfil[\"ana\"]`. Mira el bloque `moved` (módulo 12) o `terraform state mv`.",
  "solucion": ("hcl", """resource "local_file" "perfil" {
  for_each = toset(["ana", "luis"])
  filename = "${path.module}/${each.key}.txt"
  content  = "Perfil de ${each.key}"
}

moved {
  from = local_file.perfil[0]
  to   = local_file.perfil["ana"]
}

moved {
  from = local_file.perfil[1]
  to   = local_file.perfil["luis"]
}
# terraform plan → "has moved to ..." y 0 to add, 0 to destroy""")},
]
