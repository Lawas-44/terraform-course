# -*- coding: utf-8 -*-
# Módulo 11 · Módulos

LECCION = [
 ("h", "Qué es un módulo"),
 ("p", "Un **módulo** es una carpeta con archivos `.tf`. ¡Ya has estado usando uno! La carpeta donde ejecutas Terraform es el **root module**. Cuando desde ella llamas a otra carpeta, esa otra es un **child module**."),
 ("p", "Los módulos son a Terraform lo que las funciones a la programación:"),
 ("table", ["Función", "Módulo"], [
  ["Parámetros", "`variable`"],
  ["Cuerpo", "`resource`, `data`, `locals`"],
  ["Valor de retorno", "`output`"],
  ["Llamada", "bloque `module`"],
 ]),
 ("p", "Sirven para **no repetir código**, **encapsular buenas prácticas** (un bucket que siempre está cifrado y sin acceso público) y **dar a otros equipos piezas probadas**."),

 ("h", "Crear tu primer módulo"),
 ("p", "Vamos a crear un módulo que monta una **web estática en S3**. Estructura:"),
 ("code", "text", "estructura", """11-modulos/
├── main.tf                    ← root module (lo que ejecutas)
├── outputs.tf
└── modules/
    └── static-site/           ← child module
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        ├── versions.tf
        └── README.md"""),
 ("code", "hcl", "modules/static-site/variables.tf", """variable "nombre" {
  description = "Nombre base del sitio (se usa como prefijo del bucket)"
  type        = string
}

variable "entorno" {
  description = "Entorno: dev o prod"
  type        = string
  default     = "dev"
}

variable "index_html" {
  description = "Contenido HTML de la página principal"
  type        = string
  default     = "<h1>Funciona</h1>"
}

variable "etiquetas" {
  description = "Etiquetas adicionales"
  type        = map(string)
  default     = {}
}"""),
 ("code", "hcl", "modules/static-site/main.tf", """resource "aws_s3_bucket" "this" {
  bucket_prefix = "${var.nombre}-${var.entorno}-"
  force_destroy = true
  tags          = merge(var.etiquetas, { Entorno = var.entorno })
}

resource "aws_s3_bucket_website_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  index_document {
    suffix = "index.html"
  }
}

# Para una web pública hay que permitir políticas públicas en este bucket
resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "lectura_publica" {
  bucket = aws_s3_bucket.this.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "LecturaPublica"
      Effect    = "Allow"
      Principal = "*"
      Action    = "s3:GetObject"
      Resource  = "${aws_s3_bucket.this.arn}/*"
    }]
  })

  depends_on = [aws_s3_bucket_public_access_block.this]
}

resource "aws_s3_object" "index" {
  bucket       = aws_s3_bucket.this.id
  key          = "index.html"
  content      = var.index_html
  content_type = "text/html"
}"""),
 ("code", "hcl", "modules/static-site/outputs.tf", """output "nombre_bucket" {
  description = "Nombre del bucket creado"
  value       = aws_s3_bucket.this.bucket
}

output "url" {
  description = "URL pública de la web"
  value       = "http://${aws_s3_bucket_website_configuration.this.website_endpoint}"
}"""),
 ("code", "hcl", "modules/static-site/versions.tf", """terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"   # en módulos, restricciones amplias
    }
  }
}"""),
 ("tip", "Cuando un módulo tiene un recurso «principal» de cada tipo, la convención es llamarlo `this` (`aws_s3_bucket.this`)."),

 ("h", "Usar el módulo"),
 ("p", "Desde el root module se llama con un bloque `module`. `source` indica dónde está; el resto de argumentos son sus variables:"),
 ("code", "hcl", "main.tf (root)", """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

module "web" {
  source = "./modules/static-site"

  nombre     = "curso"
  entorno    = "dev"
  index_html = "<h1>Mi primera web con un módulo</h1>"
}"""),
 ("code", "hcl", "outputs.tf (root)", """output "url_web" {
  value = module.web.url   # module.NOMBRE.OUTPUT
}"""),
 ("term", """$ terraform init
Initializing modules...
- web in modules/static-site
...
$ terraform apply
...
Plan: 5 to add, 0 to change, 0 to destroy.
...
Outputs:
url_web = "http://curso-dev-2026111911...s3-website-eu-west-1.amazonaws.com"

$ terraform state list
module.web.aws_s3_bucket.this
module.web.aws_s3_bucket_policy.lectura_publica
module.web.aws_s3_bucket_public_access_block.this
module.web.aws_s3_bucket_website_configuration.this
module.web.aws_s3_object.index"""),
 ("info", "Cada vez que añades un bloque `module` nuevo o cambias su `source`, hay que ejecutar `terraform init`. Si no, verás *Module not installed*."),
 ("p", "Los recursos del módulo están **encapsulados**: desde el root no puedes escribir `aws_s3_bucket.this`; solo puedes acceder a lo que el módulo expone en sus outputs."),

 ("h", "Reutilizar: varias instancias del módulo"),
 ("p", "Aquí está la magia: con `for_each` creas tantas webs como quieras con el mismo código:"),
 ("code", "hcl", "main.tf (root)", """variable "sitios" {
  default = {
    dev  = "<h1>Entorno de desarrollo</h1>"
    prod = "<h1>Producción</h1>"
  }
}

module "web" {
  source   = "./modules/static-site"
  for_each = var.sitios

  nombre     = "curso"
  entorno    = each.key
  index_html = each.value
}

output "urls" {
  value = { for k, m in module.web : k => m.url }
}"""),

 ("h", "Módulos del Terraform Registry"),
 ("p", "No hace falta reinventar la rueda. El Registry tiene miles de módulos públicos. Los de **terraform-aws-modules** son los más usados para AWS. Por ejemplo, una VPC completa con subredes públicas, privadas y NAT en pocas líneas:"),
 ("code", "hcl", "vpc.tf", """module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"   # ¡fija SIEMPRE la versión!

  name = "curso-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]

  enable_nat_gateway = false   # el NAT Gateway cuesta ~35 €/mes; actívalo solo si lo necesitas
}

output "subredes_publicas" {
  value = module.vpc.public_subnets
}"""),
 ("p", "Cómo evaluar un módulo público antes de usarlo: número de descargas, fecha de la última versión, issues abiertos, que tenga ejemplos y que su README documente entradas y salidas. Y **lee el código**: es tu infraestructura."),

 ("h", "Fuentes de módulos y versiones"),
 ("table", ["Fuente", "Ejemplo de source"], [
  ["Carpeta local", "`./modules/static-site`"],
  ["Terraform Registry", "`terraform-aws-modules/vpc/aws` + `version`"],
  ["GitHub", "`github.com/mi-org/terraform-modulos//static-site?ref=v1.2.0`"],
  ["Git genérico", "`git::https://gitlab.com/org/modulos.git//red?ref=v2.0.0`"],
  ["Registro privado", "`app.terraform.io/mi-org/static-site/aws` + `version`"],
 ]),
 ("ul", [
  "`//` separa el repositorio de la subcarpeta del módulo.",
  "`?ref=` fija una etiqueta, rama o commit de Git. Usa siempre **etiquetas de versión** (`v1.2.0`), no `main`.",
  "Versiona tus módulos con **SemVer**: MAYOR (rompe compatibilidad), MENOR (añade funciones), PARCHE (arreglos).",
 ]),

 ("h", "Buenas prácticas al diseñar módulos"),
 ("ul", [
  "**Una responsabilidad clara**: «red», «web estática», «base de datos». No un módulo que lo hace todo.",
  "**No envuelvas un único recurso** sin añadir valor: un módulo que solo crea un `aws_s3_bucket` con los mismos argumentos no aporta nada.",
  "**No configures providers dentro** de un módulo reutilizable: deja que los herede del root (o pásaselos con `providers = { aws = aws.virginia }`).",
  "Todas las variables con `description` y `type`; valores por defecto sensatos y seguros.",
  "Outputs para todo lo que otro pueda necesitar (IDs, ARNs, URLs).",
  "Un `README.md` y una carpeta `examples/` con un uso mínimo.",
  "Genera la documentación automáticamente con **terraform-docs**:",
 ]),
 ("code", "bash", "terminal", """terraform-docs markdown table ./modules/static-site > ./modules/static-site/README.md"""),
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
