# -*- coding: utf-8 -*-
# Módulo 11 · Módulos

LECCION = [
 ("h", "Qué es un módulo"),
 ("p", "Un **módulo** es una carpeta con archivos `.tf` que puedes **reutilizar**. Es como una receta: la escribes una vez y la usas todas las veces que quieras con ingredientes distintos."),
 ("ul", [
  "La carpeta donde ejecutas Terraform se llama **módulo raíz** (*root module*).",
  "Las carpetas que llamas desde ella son **módulos hijos** (*child modules*).",
 ]),
 ("table", ["Parte del módulo", "Para qué sirve"], [
  ["`variable`", "Los datos que recibe"],
  ["`resource`", "Lo que crea"],
  ["`output`", "Los datos que devuelve"],
 ]),

 ("h", "Crear un módulo"),
 ("p", "Vamos a crear un módulo que monta una **página web en S3**. La estructura:"),
 ("code", "text", "estructura", """11-modulos/
├── main.tf                  # módulo raíz: aquí usamos el módulo
└── modules/
    └── static-site/         # nuestro módulo
        ├── variables.tf
        ├── main.tf
        └── outputs.tf"""),
 ("code", "hcl", "modules/static-site/variables.tf", """variable "nombre" {
  description = "Nombre de la web"
  type        = string
}

variable "index_html" {
  description = "Contenido de la página principal"
  type        = string
  default     = "<h1>Funciona</h1>"
}"""),
 ("code", "hcl", "modules/static-site/main.tf", """resource "aws_s3_bucket" "this" {
  bucket_prefix = "${var.nombre}-"
  force_destroy = true
}

# Activar el modo "página web" del bucket
resource "aws_s3_bucket_website_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  index_document {
    suffix = "index.html"
  }
}

# Permitir que la web sea pública
resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "publica" {
  bucket = aws_s3_bucket.this.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.this.arn}/*"
    }]
  })
  depends_on = [aws_s3_bucket_public_access_block.this]
}

# Subir la página
resource "aws_s3_object" "index" {
  bucket       = aws_s3_bucket.this.id
  key          = "index.html"
  content      = var.index_html
  content_type = "text/html"
}"""),
 ("code", "hcl", "modules/static-site/outputs.tf", """output "url" {
  description = "Dirección de la web"
  value       = "http://${aws_s3_bucket_website_configuration.this.website_endpoint}"
}"""),

 ("h", "Usar el módulo"),
 ("p", "Desde el módulo raíz se usa con un bloque `module`. En `source` va la carpeta, y después los valores de sus variables:"),
 ("code", "hcl", "main.tf", """provider "aws" {
  region = "eu-west-1"
}

module "web" {
  source     = "./modules/static-site"
  nombre     = "curso"
  index_html = "<h1>Mi primera web con un módulo</h1>"
}

output "url_web" {
  value = module.web.url
}"""),
 ("p", "Para leer un output del módulo se escribe `module.NOMBRE.OUTPUT`, en este caso `module.web.url`."),
 ("term", """$ terraform init
Initializing modules...
- web in modules/static-site
$ terraform apply
...
Outputs:
url_web = "http://curso-2026111911...s3-website-eu-west-1.amazonaws.com\""""),
 ("info", "Cada vez que añades un módulo nuevo hay que ejecutar `terraform init`."),
 ("p", "Desde fuera del módulo **no puedes** usar directamente sus recursos (por ejemplo `aws_s3_bucket.this`). Solo puedes usar lo que el módulo devuelve en sus outputs."),

 ("h", "Reutilizar el módulo varias veces"),
 ("p", "Con `for_each` creas varias webs con el mismo módulo:"),
 ("code", "hcl", "main.tf", """module "web" {
  source   = "./modules/static-site"
  for_each = {
    dev  = "<h1>Desarrollo</h1>"
    prod = "<h1>Producción</h1>"
  }

  nombre     = "curso-${each.key}"
  index_html = each.value
}"""),

 ("h", "Módulos hechos por otros"),
 ("p", "En el Terraform Registry hay miles de módulos públicos listos para usar. Por ejemplo, este crea una red completa en AWS:"),
 ("code", "hcl", "vpc.tf", """module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "curso-vpc"
  cidr = "10.0.0.0/16"

  azs            = ["eu-west-1a", "eu-west-1b"]
  public_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
}"""),
 ("warn", "Indica siempre la versión (`version`). Si no, un día podrías descargar una versión nueva que cambie cosas sin avisar."),
 ("p", "Un módulo también puede venir de un repositorio de GitHub. En ese caso la versión se indica con `?ref=`:"),
 ("code", "hcl", "módulo desde GitHub", """module "red" {
  source = "github.com/mi-usuario/terraform-modulos//red?ref=v1.0.0"
}"""),
 ("p", "La doble barra `//` separa el repositorio de la carpeta del módulo."),

 ("h", "Consejos para crear buenos módulos"),
 ("ul", [
  "Que hagan **una sola cosa** clara (una red, una web, una base de datos).",
  "Variables con `description` y `type`.",
  "Outputs con todo lo que otros puedan necesitar.",
  "No pongas bloques `provider` dentro del módulo: deja que los reciba del módulo raíz.",
  "Añade un `README.md` explicando cómo usarlo.",
 ]),
]

TEST = [
 ("¿Qué es el root module?",
  ["Un módulo del Registry", "La carpeta donde ejecutas los comandos de Terraform", "El módulo de AWS", "Un módulo con permisos de root"], 1,
  "Toda configuración tiene un root module; los demás son child modules."),
 ("¿Cómo lees el output `url` de un bloque `module \"web\"`?",
  ["web.url", "module.web.url", "output.web.url", "var.web.url"], 1, "Sintaxis: module.NOMBRE.OUTPUT."),
 ("Desde el root, ¿puedes referenciar directamente `aws_s3_bucket.this` creado dentro de un módulo?",
  ["Sí", "No, solo los outputs que exponga el módulo", "Solo con depends_on", "Solo en el mismo archivo"], 1,
  "Los módulos encapsulan sus recursos; la interfaz son las variables y los outputs."),
 ("Has añadido un bloque `module` nuevo. ¿Qué tienes que hacer antes de `plan`?",
  ["Nada", "terraform init", "terraform state push", "terraform fmt"], 1, "init descarga o registra los módulos."),
 ("¿Qué es lo correcto al usar un módulo del Registry?",
  ["No poner version para tener siempre la última", "Fijar version (p. ej. \"~> 6.0\")", "Copiar el código a mano", "Usar ?ref=main"], 1,
  "Fijar la versión evita cambios inesperados al hacer init."),
 ("¿Qué indica `//modules/red` en `github.com/org/repo//modules/red?ref=v1.0.0`?",
  ["Un comentario", "La subcarpeta del repositorio donde está el módulo", "La rama", "El provider"], 1,
  "`//` separa el repositorio de la ruta del módulo; `ref` es la versión."),
 ("¿Por qué no se debe declarar un bloque `provider` dentro de un módulo reutilizable?",
  ["Porque no funciona", "Porque impide al llamante elegir región/cuenta y complica usar count/for_each con el módulo", "Por rendimiento", "Porque es más caro"], 1,
  "Los módulos deben heredar los providers del root (o recibirlos con el argumento providers)."),
]

RETOS = [
 {"titulo": "Módulo de etiquetado (sin nube)",
  "enunciado": "Crea un módulo `modules/etiquetas` que reciba `proyecto`, `entorno` y `extra` (map) y devuelva un output `todas` con las etiquetas combinadas más `Gestion = \"terraform\"`, y un output `prefijo` = `proyecto-entorno`. Úsalo desde el root y muestra ambos outputs.",
  "pista": "Un módulo puede no tener recursos: solo variables, locals y outputs.",
  "solucion": ("hcl", """# modules/etiquetas/main.tf
variable "proyecto" { type = string }
variable "entorno" { type = string }
variable "extra" {
  type    = map(string)
  default = {}
}

output "prefijo" {
  value = "${var.proyecto}-${var.entorno}"
}

output "todas" {
  value = merge(var.extra, {
    Proyecto = var.proyecto
    Entorno  = var.entorno
    Gestion  = "terraform"
  })
}

# main.tf (root)
module "tags" {
  source   = "./modules/etiquetas"
  proyecto = "tienda"
  entorno  = "dev"
  extra    = { Equipo = "web" }
}

output "etiquetas" {
  value = module.tags.todas
}""")},
 {"titulo": "Mejora el módulo static-site",
  "enunciado": "Añade al módulo una variable opcional `error_html` que, si se proporciona, cree `error.html` y lo configure como documento de error. Si es null, no se crea nada.",
  "pista": "`count = var.error_html == null ? 0 : 1` en el objeto y un bloque `dynamic \"error_document\"` en la configuración web.",
  "solucion": ("hcl", """variable "error_html" {
  type    = string
  default = null
}

resource "aws_s3_object" "error" {
  count        = var.error_html == null ? 0 : 1
  bucket       = aws_s3_bucket.this.id
  key          = "error.html"
  content      = var.error_html
  content_type = "text/html"
}

resource "aws_s3_bucket_website_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  index_document {
    suffix = "index.html"
  }

  dynamic "error_document" {
    for_each = var.error_html == null ? [] : [1]
    content {
      key = "error.html"
    }
  }
}""")},
]
