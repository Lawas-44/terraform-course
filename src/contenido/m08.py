# -*- coding: utf-8 -*-
# Módulo 08 · Expresiones y funciones

LECCION = [
 ("h", "Operadores"),
 ("p", "HCL tiene los operadores habituales. Pruébalos todos en `terraform console`:"),
 ("table", ["Tipo", "Operadores", "Ejemplo", "Resultado"], [
  ["Aritméticos", "`+ - * / %`", "`10 % 3`", "`1`"],
  ["Comparación", "`== != < > <= >=`", "`5 >= 3`", "`true`"],
  ["Lógicos", "`&& || !`", "`true && !false`", "`true`"],
 ]),

 ("h", "Condicionales"),
 ("p", "La única estructura condicional es el **operador ternario**: `condición ? valor_si_true : valor_si_false`."),
 ("code", "hcl", "condicionales", """variable "entorno" {
  type    = string
  default = "dev"
}

locals {
  es_prod        = var.entorno == "prod"
  tipo_instancia = local.es_prod ? "t3.medium" : "t3.micro"
  replicas       = local.es_prod ? 3 : 1
  dominio        = local.es_prod ? "midominio.com" : "${var.entorno}.midominio.com"
}"""),
 ("warn", "Las dos ramas deben devolver el **mismo tipo**. `local.es_prod ? 3 : \"uno\"` da error *Inconsistent conditional result types*."),

 ("h", "Expresiones for"),
 ("p", "Las expresiones `for` transforman colecciones. Si van entre `[ ]` devuelven una **lista**; entre `{ }`, un **map**:"),
 ("code", "hcl", "for", """locals {
  nombres = ["ana", "luis", "marta"]

  # lista → lista
  mayusculas = [for n in local.nombres : upper(n)]
  # ["ANA", "LUIS", "MARTA"]

  # con filtro if
  largos = [for n in local.nombres : n if length(n) > 3]
  # ["luis", "marta"]

  # con índice
  numerados = [for i, n in local.nombres : "${i + 1}. ${n}"]
  # ["1. ana", "2. luis", "3. marta"]

  # lista → map
  longitudes = { for n in local.nombres : n => length(n) }
  # { ana = 3, luis = 4, marta = 5 }

  # map → map
  precios     = { cafe = 1.5, te = 1.2, zumo = 3 }
  con_iva     = { for k, v in local.precios : k => v * 1.21 }
  solo_caros  = { for k, v in local.precios : k => v if v > 2 }
}"""),
 ("p", "Un caso muy práctico: convertir una lista de objetos en un map para usarlo con `for_each`:"),
 ("code", "hcl", "lista de objetos → map", """variable "buckets" {
  default = [
    { nombre = "fotos", versionado = true },
    { nombre = "logs",  versionado = false },
  ]
}

resource "aws_s3_bucket" "this" {
  for_each      = { for b in var.buckets : b.nombre => b }
  bucket_prefix = "${each.key}-"
}"""),

 ("h", "Splat"),
 ("p", "El operador **splat** `[*]` es un atajo para sacar un atributo de todos los elementos de una lista:"),
 ("code", "hcl", "splat", """resource "aws_instance" "web" {
  count         = 3
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
}

output "ips" {
  value = aws_instance.web[*].public_ip
  # equivale a: [for i in aws_instance.web : i.public_ip]
}"""),
 ("info", "El splat solo funciona con listas (recursos con `count`). Para recursos con `for_each` (que son maps) usa una expresión `for` o `values(recurso)[*].atributo`."),

 ("h", "Bloques dynamic"),
 ("p", "Algunos recursos tienen **bloques anidados** que se repiten (reglas, etiquetas, ajustes). `dynamic` los genera a partir de una colección:"),
 ("code", "hcl", "dynamic", """variable "puertos" {
  type    = list(number)
  default = [80, 443, 8080]
}

resource "aws_security_group" "web" {
  name_prefix = "web-"

  dynamic "ingress" {
    for_each = var.puertos
    content {
      description = "Puerto ${ingress.value}"
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
# Genera 3 bloques ingress { ... }"""),
 ("p", "Dentro de `content`, el iterador se llama como el bloque (`ingress.value`, `ingress.key`). Puedes renombrarlo con `iterator = puerto`."),
 ("tip", "No abuses de `dynamic`: el código se vuelve difícil de leer. Si solo son dos bloques fijos, escríbelos a mano."),

 ("h", "Funciones integradas"),
 ("p", "Terraform trae más de 100 funciones. **No puedes crear las tuyas propias** (salvo las que aporten algunos providers). Estas son las que más usarás:"),
 ("table", ["Función", "Ejemplo", "Resultado"], [
  ["`upper` / `lower`", "`lower(\"WEB\")`", "`\"web\"`"],
  ["`format`", "`format(\"app-%03d\", 7)`", "`\"app-007\"`"],
  ["`join` / `split`", "`join(\",\", [\"a\",\"b\"])`", "`\"a,b\"`"],
  ["`replace`", "`replace(\"a_b\", \"_\", \"-\")`", "`\"a-b\"`"],
  ["`substr`", "`substr(\"terraform\", 0, 5)`", "`\"terra\"`"],
  ["`length`", "`length([1,2,3])`", "`3`"],
  ["`contains`", "`contains([\"a\",\"b\"], \"b\")`", "`true`"],
  ["`concat`", "`concat([1], [2,3])`", "`[1,2,3]`"],
  ["`flatten`", "`flatten([[1,2],[3]])`", "`[1,2,3]`"],
  ["`distinct`", "`distinct([1,1,2])`", "`[1,2]`"],
  ["`merge`", "`merge({a=1}, {b=2})`", "`{a=1, b=2}`"],
  ["`lookup`", "`lookup({a=1}, \"b\", 0)`", "`0`"],
  ["`keys` / `values`", "`keys({a=1, b=2})`", "`[\"a\",\"b\"]`"],
  ["`toset` / `tolist`", "`toset([\"a\",\"a\"])`", "`[\"a\"]`"],
  ["`min` / `max`", "`max(3, 7, 2)`", "`7`"],
  ["`coalesce`", "`coalesce(\"\", \"defecto\")`", "`\"defecto\"`"],
  ["`try`", "`try(var.x.campo, \"n/a\")`", "valor o `\"n/a\"`"],
  ["`cidrsubnet`", "`cidrsubnet(\"10.0.0.0/16\", 8, 2)`", "`\"10.0.2.0/24\"`"],
  ["`jsonencode`", "`jsonencode({a=1})`", "`\"{\\\"a\\\":1}\"`"],
  ["`file`", "`file(\"${path.module}/script.sh\")`", "contenido del archivo"],
  ["`templatefile`", "ver abajo", "texto renderizado"],
  ["`timestamp`", "`timestamp()`", "fecha actual (cambia en cada plan)"],
 ]),

 ("h", "Funciones de red: cidrsubnet"),
 ("p", "`cidrsubnet(prefijo, bits_nuevos, número)` divide una red en subredes. Con una VPC `/16` y 8 bits nuevos obtienes subredes `/24`:"),
 ("code", "hcl", "subredes automáticas", """locals {
  vpc_cidr = "10.0.0.0/16"
  zonas    = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]

  subredes_publicas = {
    for i, az in local.zonas : az => cidrsubnet(local.vpc_cidr, 8, i)
  }
  # { eu-west-1a = "10.0.0.0/24", eu-west-1b = "10.0.1.0/24", eu-west-1c = "10.0.2.0/24" }

  subredes_privadas = {
    for i, az in local.zonas : az => cidrsubnet(local.vpc_cidr, 8, i + 10)
  }
  # { eu-west-1a = "10.0.10.0/24", ... }
}"""),

 ("h", "Plantillas: templatefile y jsonencode"),
 ("p", "Para textos largos (scripts, configuraciones) es mejor tenerlos en archivos aparte y rellenarlos con `templatefile`:"),
 ("code", "bash", "templates/user_data.sh.tftpl", """#!/bin/bash
dnf install -y nginx
cat > /usr/share/nginx/html/index.html <<HTML
<h1>${titulo}</h1>
<ul>
%{ for s in servicios ~}
  <li>${s}</li>
%{ endfor ~}
</ul>
HTML
systemctl enable --now nginx"""),
 ("code", "hcl", "main.tf", """resource "aws_instance" "web" {
  # ...
  user_data = templatefile("${path.module}/templates/user_data.sh.tftpl", {
    titulo    = "Entorno ${var.entorno}"
    servicios = ["web", "api", "worker"]
  })
}"""),
 ("p", "Y para JSON (por ejemplo, políticas IAM), **nunca escribas JSON a mano dentro de un string**: usa `jsonencode`, que garantiza que sea válido:"),
 ("code", "hcl", "política IAM con jsonencode", """resource "aws_iam_policy" "lectura_s3" {
  name = "lectura-s3"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.demo.arn,
        "${aws_s3_bucket.demo.arn}/*",
      ]
    }]
  })
}"""),

 ("h", "Manejo de errores: try, can y coalesce"),
 ("code", "hcl", "valores opcionales", """variable "config" {
  type    = any
  default = { nombre = "web" }
}

locals {
  # try: devuelve la primera expresión que no falle
  puerto = try(var.config.puerto, 80)              # 80, porque no existe

  # can: true/false según si la expresión funciona (útil en validaciones)
  es_ip = can(regex("^\\\\d+\\\\.\\\\d+\\\\.\\\\d+\\\\.\\\\d+$", "10.0.0.1"))  # true

  # coalesce: primer valor no nulo ni vacío
  nombre = coalesce(var.nombre_personalizado, "nombre-por-defecto")
}"""),
]

TEST = [
 ("¿Qué devuelve `[for n in [\"a\", \"bb\", \"ccc\"] : length(n)]`?",
  ["[\"a\", \"bb\", \"ccc\"]", "[1, 2, 3]", "3", "{a = 1, bb = 2, ccc = 3}"], 1, "Una lista con la longitud de cada string."),
 ("¿Qué devuelve `{ for n in [\"a\", \"bb\"] : n => upper(n) }`?",
  ["[\"A\", \"BB\"]", "{ a = \"A\", bb = \"BB\" }", "Error", "{ \"A\", \"BB\" }"], 1, "Con llaves y `=>` se construye un map."),
 ("¿Qué devuelve `cidrsubnet(\"10.0.0.0/16\", 8, 5)`?",
  ["10.0.5.0/24", "10.5.0.0/16", "10.0.0.5/24", "10.0.8.0/21"], 0, "/16 + 8 bits = /24; la subred número 5 es 10.0.5.0/24."),
 ("¿Por qué `var.x ? 1 : \"no\"` da error?",
  ["Falta un if", "Las dos ramas devuelven tipos distintos", "No se puede usar var en condicionales", "Faltan paréntesis"], 1,
  "Ambas ramas deben ser del mismo tipo (o convertibles)."),
 ("¿Para qué sirve un bloque `dynamic`?",
  ["Para crear varios recursos", "Para generar bloques anidados repetidos dentro de un recurso", "Para cargar archivos", "Para variables dinámicas"], 1,
  "Genera bloques como `ingress`, `setting`… a partir de una colección."),
 ("¿Cuál es la mejor forma de escribir una política IAM en Terraform?",
  ["Un heredoc con JSON escrito a mano", "jsonencode() con un objeto HCL", "Un archivo .txt", "Un comentario"], 1,
  "jsonencode garantiza JSON válido y permite usar referencias y expresiones."),
 ("¿Qué devuelve `try(local.mapa.no_existe, \"defecto\")`?",
  ["Error", "null", "\"defecto\"", "\"no_existe\""], 2, "`try` devuelve la primera expresión que se evalúa sin error."),
]

RETOS = [
 {"titulo": "Plan de direcciones IP",
  "enunciado": "Dada la VPC `10.20.0.0/16` y las zonas `a`, `b`, `c`, genera en `locals` un map con, para cada zona, un objeto `{ publica = ..., privada = ... }`. Las públicas deben ser 10.20.0-2.0/24 y las privadas 10.20.100-102.0/24. Compruébalo en `terraform console`.",
  "pista": "`cidrsubnet(cidr, 8, i)` y `cidrsubnet(cidr, 8, i + 100)` dentro de un `for` con índice.",
  "solucion": ("hcl", """locals {
  cidr  = "10.20.0.0/16"
  zonas = ["a", "b", "c"]

  red = {
    for i, z in local.zonas : z => {
      publica = cidrsubnet(local.cidr, 8, i)
      privada = cidrsubnet(local.cidr, 8, i + 100)
    }
  }
}
# > local.red.b
# { privada = "10.20.101.0/24", publica = "10.20.1.0/24" }""")},
 {"titulo": "Etiquetas normalizadas",
  "enunciado": "Recibes `var.etiquetas = { \"Centro Coste\" = \"1234\", \"OWNER\" = \"Ana\" }`. Genera un map con las claves en minúsculas y con guiones en vez de espacios, y añade siempre `gestion = \"terraform\"`.",
  "pista": "`replace(lower(k), \" \", \"-\")` dentro de un `for`, y `merge` al final.",
  "solucion": ("hcl", """variable "etiquetas" {
  type = map(string)
  default = {
    "Centro Coste" = "1234"
    "OWNER"        = "Ana"
  }
}

locals {
  etiquetas_normalizadas = merge(
    { for k, v in var.etiquetas : replace(lower(k), " ", "-") => v },
    { gestion = "terraform" }
  )
}
# { "centro-coste" = "1234", gestion = "terraform", owner = "Ana" }""")},
]
