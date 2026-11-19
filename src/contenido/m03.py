# -*- coding: utf-8 -*-
# Módulo 03 · El lenguaje HCL

LECCION = [
 ("h", "Los bloques"),
 ("p", "El lenguaje de Terraform se llama **HCL**. Todo se escribe en **bloques**. Un bloque tiene un tipo, unas etiquetas entre comillas y un contenido entre llaves `{ }`:"),
 ("code", "hcl", "anatomía de un bloque", """# tipo      etiqueta 1     etiqueta 2
resource    "local_file"   "saludo" {
  filename = "saludo.txt"   # argumento: nombre = valor
  content  = "hola"
}"""),
 ("p", "Los bloques que más vas a usar:"),
 ("table", ["Bloque", "Para qué sirve"], [
  ["`resource`", "Algo que Terraform crea"],
  ["`data`", "Algo que ya existe y Terraform solo consulta"],
  ["`variable`", "Un dato de entrada que se puede cambiar"],
  ["`output`", "Un dato que se muestra al terminar"],
  ["`locals`", "Valores de ayuda para no repetir"],
  ["`provider`", "Configura un provider (por ejemplo, la región de AWS)"],
  ["`terraform`", "Ajustes de Terraform (versiones y providers)"],
 ]),

 ("h", "Tipos de datos"),
 ("p", "Los valores pueden ser de varios tipos:"),
 ("code", "hcl", "tipos.tf", """locals {
  texto  = "hola"                        # texto, siempre con comillas dobles
  numero = 42                            # número
  activo = true                          # verdadero o falso
  lista  = ["a", "b", "c"]               # lista de valores
  mapa   = { entorno = "dev", equipo = "web" }  # pares nombre = valor
  grupo  = toset(["a", "b", "a"])        # conjunto: sin orden y sin repetidos -> ["a", "b"]
}"""),
 ("p", "Para leer un elemento:"),
 ("code", "hcl", "leer valores", """local.lista[0]       # "a"  (se empieza a contar desde 0)
local.mapa.entorno   # "dev\""""),
 ("warn", "Usa siempre comillas dobles. `'hola'` con comillas simples da error."),

 ("h", "Meter valores dentro de un texto"),
 ("p", "Con `${ }` puedes meter un valor dentro de un texto:"),
 ("code", "hcl", "interpolación", """locals {
  proyecto = "tienda"
  entorno  = "dev"
  nombre   = "${local.proyecto}-${local.entorno}"   # "tienda-dev"
}"""),
 ("p", "Para textos de varias líneas se usa `<<-EOT` ... `EOT`:"),
 ("code", "hcl", "texto de varias líneas", """resource "local_file" "config" {
  filename = "app.conf"
  content  = <<-EOT
    proyecto = ${local.proyecto}
    entorno  = ${local.entorno}
  EOT
}"""),

 ("h", "Usar datos de otro recurso"),
 ("p", "Un recurso puede usar datos de otro. Se escribe `TIPO.NOMBRE.DATO`:"),
 ("code", "hcl", "referencias.tf", """resource "random_integer" "puerto" {
  min = 8000
  max = 8999
}

resource "local_file" "env" {
  filename = ".env"
  content  = "PORT=${random_integer.puerto.result}"
}"""),
 ("p", "Aquí `local_file.env` usa el número que ha generado `random_integer.puerto`. Terraform entiende que primero tiene que crear el número."),
 ("tip", "¿Qué datos tiene cada recurso? Búscalo en registry.terraform.io, en la página del recurso, en el apartado *Attribute Reference*."),

 ("h", "Comentarios y organización"),
 ("p", "Los comentarios empiezan por `#`. Terraform los ignora; sirven para explicar el código."),
 ("p", "Terraform junta todos los `.tf` de la carpeta, así que puedes repartir el código en varios archivos. Lo habitual es:"),
 ("code", "text", "estructura", """mi-proyecto/
├── main.tf        # recursos
├── variables.tf   # variables
├── outputs.tf     # outputs
└── versions.tf    # bloque terraform { }"""),

 ("h", "Ordenar y comprobar el código"),
 ("p", "Dos comandos te ayudan a tener el código limpio y sin errores:"),
 ("term", """$ terraform fmt
main.tf
$ terraform validate
Success! The configuration is valid."""),
 ("ul", [
  "`terraform fmt` ordena el código (sangría y alineación).",
  "`terraform validate` busca errores sin crear nada.",
  "`terraform fmt -check` no cambia nada: solo avisa si hay archivos sin ordenar. Se usa en revisiones automáticas.",
 ]),
 ("p", "Así se ve un error. Te dice el archivo, la línea y, muchas veces, cómo arreglarlo:"),
 ("term", """$ terraform validate
Error: Unsupported argument

  on main.tf line 3, in resource "local_file" "saludo":
   3:   file_name = "saludo.txt"

An argument named "file_name" is not expected here. Did you mean "filename"?"""),

 ("tip", "Si un comando falla y necesitas más detalle, activa los registros con la variable de entorno `TF_LOG`: por ejemplo `export TF_LOG=DEBUG` antes de ejecutar Terraform."),

 ("h", "La consola de Terraform"),
 ("p", "`terraform console` te deja probar valores y operaciones. Muy útil para aprender:"),
 ("term", """$ terraform console
> local.lista[1]
"b"
> upper("hola")
"HOLA"
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
