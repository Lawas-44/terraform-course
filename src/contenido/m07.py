# -*- coding: utf-8 -*-
# Módulo 07 · Meta-argumentos

LECCION = [
 ("h", "Qué son los meta-argumentos"),
 ("p", "Además de sus argumentos propios, **cualquier** bloque `resource` acepta cinco argumentos especiales que cambian cómo lo trata Terraform:"),
 ("table", ["Meta-argumento", "Para qué sirve"], [
  ["`count`", "Crear N copias numeradas"],
  ["`for_each`", "Crear una copia por cada elemento de un map o set"],
  ["`depends_on`", "Dependencias explícitas (módulo 6)"],
  ["`provider`", "Elegir un provider con alias (módulo 5)"],
  ["`lifecycle`", "Cambiar cómo se crea, actualiza o destruye"],
 ]),
 ("p", "Para practicar sin coste, usaremos `local_file` en los ejemplos. Todo funciona igual con recursos de AWS."),

 ("h", "count: N copias"),
 ("code", "hcl", "count.tf", """resource "local_file" "nota" {
  count    = 3
  filename = "${path.module}/nota-${count.index}.txt"
  content  = "Soy la nota número ${count.index}"
}

output "archivos" {
  value = local_file.nota[*].filename   # splat: todos los filename
}"""),
 ("ul", [
  "`count.index` vale 0, 1, 2…",
  "El recurso pasa a ser una **lista**: `local_file.nota[0]`, `local_file.nota[1]`…",
  "`local_file.nota[*].filename` (splat) devuelve una lista con el atributo de todas las copias.",
 ]),
 ("p", "Uso muy habitual: crear un recurso **solo si** se cumple una condición:"),
 ("code", "hcl", "creación condicional", """variable "crear_backup" {
  type    = bool
  default = false
}

resource "aws_s3_bucket" "backup" {
  count         = var.crear_backup ? 1 : 0
  bucket_prefix = "backup-"
}

# Como es una lista, al referenciarlo hay que tener en cuenta que puede no existir:
output "bucket_backup" {
  value = var.crear_backup ? aws_s3_bucket.backup[0].bucket : "no creado"
}"""),

 ("h", "El problema de count con listas"),
 ("p", "Crear copias a partir de una lista con `count` parece natural…"),
 ("code", "hcl", "count con lista (¡cuidado!)", """variable "usuarios" {
  default = ["ana", "luis", "marta"]
}

resource "local_file" "perfil" {
  count    = length(var.usuarios)
  filename = "${path.module}/${var.usuarios[count.index]}.txt"
  content  = "Perfil de ${var.usuarios[count.index]}"
}
# Estado: perfil[0]=ana  perfil[1]=luis  perfil[2]=marta"""),
 ("p", "…hasta que **quitas un elemento del medio**. Si eliminas `\"luis\"`, la lista pasa a ser `[\"ana\", \"marta\"]` y los índices se desplazan:"),
 ("term", """  # local_file.perfil[1] must be replaced     ← luis.txt pasa a ser marta.txt
-/+ resource "local_file" "perfil" {
      ~ filename = "./luis.txt" -> "./marta.txt" # forces replacement

  # local_file.perfil[2] will be destroyed     ← y se destruye el antiguo marta
  - resource "local_file" "perfil" {

Plan: 1 to add, 0 to change, 2 to destroy."""),
 ("p", "Con archivos da igual, pero imagina que fueran **bases de datos** de usuarios: se recrearía la de Marta y perdería sus datos. La solución es `for_each`."),

 ("h", "for_each: copias con nombre"),
 ("p", "`for_each` recibe un **set de strings** o un **map** y crea una copia por elemento, identificada por su **clave** en lugar de por un número:"),
 ("code", "hcl", "for_each con set", """variable "usuarios" {
  type    = set(string)
  default = ["ana", "luis", "marta"]
}

resource "local_file" "perfil" {
  for_each = var.usuarios
  filename = "${path.module}/${each.key}.txt"
  content  = "Perfil de ${each.value}"   # en un set, key y value son iguales
}
# Estado: perfil["ana"]  perfil["luis"]  perfil["marta"]"""),
 ("p", "Ahora, si quitas `\"luis\"`, el plan solo destruye `perfil[\"luis\"]`. Los demás no se tocan:"),
 ("term", """  # local_file.perfil["luis"] will be destroyed
  - resource "local_file" "perfil" {

Plan: 0 to add, 0 to change, 1 to destroy."""),
 ("p", "Con un **map** puedes asociar datos a cada elemento:"),
 ("code", "hcl", "for_each con map de objetos", """variable "servicios" {
  type = map(object({
    puerto = number
    replicas = number
  }))
  default = {
    web = { puerto = 80, replicas = 2 }
    api = { puerto = 8080, replicas = 3 }
  }
}

resource "local_file" "servicio" {
  for_each = var.servicios
  filename = "${path.module}/${each.key}.conf"
  content  = "puerto=${each.value.puerto}\\nreplicas=${each.value.replicas}\\n"
}

output "rutas" {
  # con for_each el recurso es un MAP: se recorre con for
  value = { for nombre, f in local_file.servicio : nombre => f.filename }
}"""),
 ("table", ["", "count", "for_each"], [
  ["Recibe", "un número", "un set(string) o un map"],
  ["Identifica copias por", "índice `[0]`", "clave `[\"web\"]`"],
  ["Variable dentro", "`count.index`", "`each.key`, `each.value`"],
  ["El recurso es", "una lista", "un map"],
  ["Úsalo para", "N copias idénticas o crear/no crear", "colecciones de cosas distintas"],
 ]),
 ("warn", "Las claves de `for_each` deben conocerse **en el plan**. No puedes usar como clave un atributo que se calcula al crear otro recurso (como un ID). Si lo haces verás el error *Invalid for_each argument*."),

 ("h", "lifecycle: controlar el ciclo de vida"),
 ("p", "El bloque `lifecycle` acepta varias opciones:"),
 ("code", "hcl", "lifecycle", """resource "aws_s3_bucket" "datos_criticos" {
  bucket_prefix = "datos-"

  lifecycle {
    # 1. Impide destruir el recurso: el plan fallará si lo intenta
    prevent_destroy = true

    # 2. Ignora cambios hechos fuera de Terraform en estos atributos
    ignore_changes = [tags["UltimaRevision"]]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"

  lifecycle {
    # 3. Si hay que reemplazarla, crea la nueva ANTES de borrar la vieja
    create_before_destroy = true

    # 4. Reemplázala cuando cambie este otro recurso
    replace_triggered_by = [aws_security_group.web]
  }
}"""),
 ("table", ["Opción", "Cuándo usarla"], [
  ["`prevent_destroy`", "Bases de datos, buckets con datos, zonas DNS: lo que no debe borrarse nunca por error"],
  ["`ignore_changes`", "Atributos que modifica otro sistema (autoescalado, etiquetas que pone otro equipo)"],
  ["`create_before_destroy`", "Evitar cortes de servicio al reemplazar (certificados, instancias tras un balanceador)"],
  ["`replace_triggered_by`", "Forzar reemplazo cuando cambia algo relacionado"],
 ]),
 ("term", """$ terraform destroy
╷
│ Error: Instance cannot be destroyed
│
│ Resource aws_s3_bucket.datos_criticos has lifecycle.prevent_destroy set,
│ but the plan calls for this resource to be destroyed.
╵"""),
 ("info", "Para destruir un recurso con `prevent_destroy`, primero tienes que quitar esa línea del código. Es intencionado: obliga a pensarlo dos veces y deja constancia en Git."),

 ("h", "Forzar un reemplazo con -replace"),
 ("p", "A veces un recurso está «roto» aunque Terraform crea que está bien (una instancia que no responde, por ejemplo). Puedes forzar que se recree:"),
 ("code", "bash", "terminal", """terraform plan  -replace="aws_instance.web"
terraform apply -replace="aws_instance.web"

# Con count / for_each, cuidado con las comillas:
terraform apply -replace='local_file.perfil["ana"]'"""),
 ("info", "En tutoriales antiguos verás `terraform taint`. Está obsoleto: usa `-replace`, que además te enseña el plan antes."),
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
