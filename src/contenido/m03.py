# -*- coding: utf-8 -*-
# Módulo 03 · El lenguaje HCL

LECCION = [
 ("h", "Anatomía de un bloque"),
 ("p", "Todo en Terraform se escribe en **HCL** (*HashiCorp Configuration Language*). Su pieza básica es el **bloque**:"),
 ("code", "hcl", "anatomía", """# TIPO       ETIQUETA 1     ETIQUETA 2
resource     "local_file"   "saludo"   {
  # CUERPO: argumentos  nombre = valor
  filename = "saludo.txt"
  content  = "hola"

  # bloque anidado (sin '=')
  lifecycle {
    prevent_destroy = false
  }
}"""),
 ("ul", [
  "**Tipo de bloque**: `resource`, `variable`, `output`… Determina qué significa el bloque.",
  "**Etiquetas**: van entre comillas. Cada tipo de bloque exige un número concreto (`resource` lleva 2: tipo de recurso y nombre; `variable` lleva 1; `locals` ninguna).",
  "**Argumentos**: `nombre = valor`. Asignan valores.",
  "**Bloques anidados**: bloques dentro de bloques, sin `=`.",
 ]),
 ("p", "Los bloques de primer nivel que usarás constantemente:"),
 ("table", ["Bloque", "Para qué sirve", "Se referencia como"], [
  ["`terraform`", "Versión requerida, providers, backend", "—"],
  ["`provider`", "Configura un provider (región, credenciales…)", "—"],
  ["`resource`", "Algo que Terraform crea y gestiona", "`TIPO.NOMBRE`"],
  ["`data`", "Algo que existe y Terraform solo lee", "`data.TIPO.NOMBRE`"],
  ["`variable`", "Parámetro de entrada", "`var.NOMBRE`"],
  ["`output`", "Valor de salida", "`module.X.NOMBRE` (desde fuera)"],
  ["`locals`", "Valores calculados internos", "`local.NOMBRE`"],
  ["`module`", "Llama a otro módulo", "`module.NOMBRE`"],
 ]),

 ("h", "Tipos de datos"),
 ("p", "HCL tiene tipos **primitivos** y **complejos**:"),
 ("code", "hcl", "tipos.tf", """locals {
  # Primitivos
  texto  = "hola"           # string (siempre comillas DOBLES)
  numero = 42               # number (enteros y decimales: 3.14)
  activo = true             # bool (true / false, sin comillas)

  # Colecciones (todos los elementos del mismo tipo)
  lista = ["a", "b", "c"]               # list: ordenada, admite repetidos
  mapa  = { entorno = "dev", equipo = "web" } # map: clave → valor
  # set: como list pero sin orden ni repetidos; se crea con toset()
  conjunto = toset(["a", "b", "a"])     # → ["a", "b"]

  # Estructurales (pueden mezclar tipos)
  objeto = {
    nombre  = "web"
    puertos = [80, 443]
    publico = true
  }
  tupla = ["web", 80, true]

  # Ausencia de valor
  nada = null
}"""),
 ("p", "Para leer elementos de una colección:"),
 ("code", "hcl", "acceso", """local.lista[0]            # "a"  (los índices empiezan en 0)
local.mapa["entorno"]     # "dev"
local.mapa.entorno        # "dev" (forma corta)
local.objeto.puertos[1]   # 443"""),
 ("tip", "Terraform convierte tipos automáticamente cuando puede: `\"5\"` se convierte a `5` si se espera un número, y `true` a `\"true\"` si se espera un string."),

 ("h", "Strings: interpolación, directivas y heredoc"),
 ("p", "Dentro de un string puedes insertar expresiones con `${ ... }`:"),
 ("code", "hcl", "interpolación", """locals {
  proyecto = "tienda"
  entorno  = "dev"
  nombre   = "${local.proyecto}-${local.entorno}"   # "tienda-dev"
  saludo   = "Hay ${length(local.lista)} elementos" # "Hay 3 elementos"
}"""),
 ("p", "Para textos de varias líneas se usa **heredoc**. Con `<<-` (con guion) se elimina la sangría común, lo que permite indentarlo bonito:"),
 ("code", "hcl", "heredoc", """resource "local_file" "config" {
  filename = "${path.module}/app.conf"
  content  = <<-EOT
    # Configuración generada por Terraform
    proyecto = ${local.proyecto}
    entorno  = ${local.entorno}
  EOT
}"""),
 ("p", "Y las **directivas** `%{ if }` y `%{ for }` permiten lógica dentro del texto:"),
 ("code", "hcl", "directivas", """locals {
  servidores = ["web1", "web2", "web3"]

  inventario = <<-EOT
    [web]
    %{ for s in local.servidores ~}
    ${s}.ejemplo.com
    %{ endfor ~}
  EOT
}"""),
 ("info", "El `~` elimina el salto de línea junto a la directiva, para que no queden líneas en blanco."),

 ("h", "Referencias entre bloques"),
 ("p", "Cada recurso expone **atributos** que otros pueden usar. La sintaxis es `TIPO.NOMBRE.ATRIBUTO`:"),
 ("code", "hcl", "referencias.tf", """resource "random_integer" "puerto" {
  min = 8000
  max = 8999
}

resource "local_file" "env" {
  filename = "${path.module}/.env"
  content  = "PORT=${random_integer.puerto.result}\\n"
}"""),
 ("p", "¿Cómo sabes qué atributos tiene un recurso? En la documentación del Registry, cada recurso tiene una sección **Argument Reference** (lo que tú escribes) y **Attribute Reference** (lo que puedes leer después)."),

 ("h", "Comentarios y organización de archivos"),
 ("code", "hcl", "comentarios", """# Comentario de una línea (el más habitual)
// También vale, pero menos común
/*
  Comentario
  de varias líneas
*/"""),
 ("p", "Terraform carga **todos** los `.tf` de la carpeta y los une; el orden de los archivos y de los bloques da igual. Por convención se reparten así:"),
 ("code", "text", "estructura recomendada", """mi-proyecto/
├── versions.tf    # bloque terraform {} (versiones y providers)
├── providers.tf   # bloques provider {}
├── main.tf        # recursos principales
├── variables.tf   # bloques variable {}
├── outputs.tf     # bloques output {}
└── locals.tf      # bloque locals {} (opcional)"""),

 ("h", "Estilo, fmt y validate"),
 ("p", "La comunidad sigue un estilo común: 2 espacios de sangría, signos `=` alineados en argumentos consecutivos, nombres en `snake_case` y sin repetir el tipo en el nombre (`aws_instance.web`, no `aws_instance.web_instance`). No hace falta hacerlo a mano:"),
 ("term", """$ terraform fmt
main.tf
$ terraform fmt -check -recursive   # en CI: falla si algo no está formateado
$ terraform validate
Success! The configuration is valid."""),
 ("p", "`validate` detecta errores de sintaxis, argumentos que no existen, referencias rotas y tipos incorrectos, **sin conectarse a ninguna nube**. Ejemplo de error típico:"),
 ("term", """$ terraform validate
╷
│ Error: Unsupported argument
│
│   on main.tf line 3, in resource "local_file" "saludo":
│    3:   file_name = "saludo.txt"
│
│ An argument named "file_name" is not expected here. Did you mean "filename"?
╵"""),
 ("tip", "Lee siempre los errores de abajo a arriba: archivo, línea y una sugerencia. Terraform suele decirte exactamente qué falla."),

 ("h", "terraform console: tu laboratorio de expresiones"),
 ("p", "`terraform console` abre una consola donde puedes evaluar cualquier expresión con los `locals`, variables y recursos de tu proyecto. Ideal para experimentar:"),
 ("term", """$ terraform console
> local.lista
[
  "a",
  "b",
  "c",
]
> upper(local.texto)
"HOLA"
> local.objeto.puertos[0] + 1
81
> exit"""),
]

TEST = [
 ("¿Cuántas etiquetas lleva un bloque `resource`?",
  ["Ninguna", "Una", "Dos: tipo de recurso y nombre local", "Tres"], 2,
  "Por ejemplo `resource \"local_file\" \"saludo\"`."),
 ("¿Cuál es una forma válida de escribir un string en HCL?",
  ["'hola'", "\"hola\"", "`hola`", "hola"], 1, "HCL solo admite comillas dobles."),
 ("¿Qué diferencia a un `set` de una `list`?",
  ["El set admite tipos mezclados", "El set no tiene orden ni elementos repetidos", "La list no tiene orden", "No hay diferencia"], 1,
  "Un set elimina duplicados y no garantiza orden; por eso no se accede por índice."),
 ("¿Cómo se referencia el atributo `result` del recurso `random_integer.puerto`?",
  ["random_integer.puerto.result", "resource.random_integer.puerto.result", "var.puerto.result", "${puerto.result}"], 0,
  "La sintaxis es TIPO.NOMBRE.ATRIBUTO. La interpolación `${}` solo es necesaria dentro de strings."),
 ("Tienes `main.tf` y `zzz.tf` en la misma carpeta. ¿En qué orden los procesa Terraform?",
  ["Primero main.tf", "Alfabético", "Los une todos; el orden no importa", "Solo lee main.tf"], 2,
  "Terraform construye un único grafo con todos los archivos .tf de la carpeta."),
 ("¿Qué hace `terraform fmt -check`?",
  ["Formatea los archivos", "Devuelve error si algún archivo no está bien formateado, sin modificarlo", "Valida la sintaxis", "Comprueba las credenciales"], 1,
  "Muy útil en CI para exigir código formateado."),
]

RETOS = [
 {"titulo": "Genera un inventario",
  "enunciado": "Crea un `locals` con un objeto `app` que tenga `nombre`, `version` (number) y una lista `servidores`. Genera con `local_file` un archivo `inventario.txt` que contenga una línea de cabecera con nombre y versión y después un servidor por línea.",
  "pista": "Combina un heredoc `<<-EOT` con una directiva `%{ for ~}`.",
  "solucion": ("hcl", """locals {
  app = {
    nombre     = "tienda"
    version    = 3
    servidores = ["web1", "web2", "api1"]
  }
}

resource "local_file" "inventario" {
  filename = "${path.module}/inventario.txt"
  content  = <<-EOT
    # ${local.app.nombre} v${local.app.version}
    %{ for s in local.app.servidores ~}
    ${s}
    %{ endfor ~}
  EOT
}""")},
 {"titulo": "Caza el error",
  "enunciado": "Este código tiene 4 errores. Encuéntralos sin ejecutarlo y luego compruébalo con `terraform validate`.",
  "codigo": ("hcl", """resource "local_file" {
  filename = 'notas.txt'
  contents = "Hola ${random_pet.mascota.id}"
}"""),
  "pista": "Fíjate en las etiquetas, las comillas, el nombre de un argumento y una referencia.",
  "solucion": ("hcl", """# 1. Falta la segunda etiqueta (nombre local)
# 2. Comillas simples → dobles
# 3. El argumento es "content", no "contents"
# 4. random_pet.mascota no está declarado
resource "random_pet" "mascota" {}

resource "local_file" "notas" {
  filename = "notas.txt"
  content  = "Hola ${random_pet.mascota.id}"
}""")},
]
