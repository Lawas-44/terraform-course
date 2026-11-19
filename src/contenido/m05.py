# -*- coding: utf-8 -*-
# Módulo 05 · Providers y conexión con la nube

LECCION = [
 ("h", "Qué es un provider"),
 ("p", "Terraform por sí solo no sabe crear nada en AWS, Azure o GitHub. Para eso usa **providers**: complementos que saben hablar con cada servicio. Hay miles en el **Terraform Registry** (registry.terraform.io)."),
 ("p", "En la página de cada provider está la documentación de todos sus recursos, con ejemplos. Es la página que más vas a consultar."),

 ("h", "Indicar el provider y su versión"),
 ("p", "Se declara dentro del bloque `terraform`:"),
 ("code", "hcl", "versions.tf", """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}"""),
 ("p", "La versión se puede indicar de varias formas:"),
 ("table", ["Escribes", "Acepta"], [
  ["`= 6.2.0`", "Solo la 6.2.0"],
  ["`>= 6.0`", "La 6.0 o cualquiera más nueva"],
  ["`~> 6.0`", "Cualquier 6.x, pero no la 7.0"],
 ]),
 ("tip", "Usa `~>`. Recibes mejoras pero evitas versiones nuevas que puedan romper tu código."),

 ("h", "El archivo .terraform.lock.hcl"),
 ("p", "Al hacer `terraform init`, Terraform elige una versión exacta y la apunta en `.terraform.lock.hcl`. Así todo el equipo usa la misma versión. Este archivo **sí se sube a Git**."),
 ("p", "Si quieres actualizar a una versión más nueva:"),
 ("term", """$ terraform init -upgrade"""),

 ("h", "Configurar AWS"),
 ("p", "El bloque `provider` dice cómo conectarse. Para AWS basta con la región:"),
 ("code", "hcl", "providers.tf", """provider "aws" {
  region = "eu-west-1"

  default_tags {
    tags = {
      Gestion = "terraform"
    }
  }
}"""),
 ("p", "`default_tags` pone esas etiquetas a todo lo que crees. Así sabrás en AWS qué ha creado Terraform."),

 ("h", "Las claves de acceso"),
 ("p", "Terraform necesita tus credenciales de AWS. **Nunca las escribas en el código.** Terraform las busca solo en el mismo sitio que la herramienta `aws` (lo configuraste en el módulo 1):"),
 ("term", """$ export AWS_PROFILE=curso-terraform
$ aws sts get-caller-identity
$ terraform plan"""),
 ("warn", "Si subes unas claves de AWS a GitHub, en pocos minutos alguien puede usarlas para gastar dinero en tu cuenta."),

 ("h", "Tu primer recurso en la nube: un bucket S3"),
 ("p", "**S3** es el almacenamiento de archivos de AWS. Un **bucket** es como una carpeta. Crear uno vacío es gratis."),
 ("code", "hcl", "main.tf", """resource "aws_s3_bucket" "demo" {
  bucket_prefix = "curso-tf-demo-"
  force_destroy = true
}

resource "aws_s3_object" "hola" {
  bucket  = aws_s3_bucket.demo.id
  key     = "hola.txt"
  content = "Subido con Terraform"
}

output "bucket" {
  value = aws_s3_bucket.demo.bucket
}"""),
 ("ul", [
  "Los nombres de bucket deben ser únicos en todo el mundo. Con `bucket_prefix`, AWS añade un final al azar para que no se repita.",
  "`force_destroy = true` permite borrar el bucket aunque tenga archivos (solo para practicar).",
  "`aws_s3_object` sube un archivo al bucket.",
 ]),
 ("term", """$ terraform init
$ terraform apply
...
Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

Outputs:
bucket = "curso-tf-demo-20261119103512345600000001"

$ aws s3 ls s3://curso-tf-demo-20261119103512345600000001
2026-11-19 10:35:14         20 hola.txt"""),
 ("p", "Busca el bucket en la web de AWS (sección S3). Cuando termines, bórralo con `terraform destroy`."),

 ("h", "Usar dos regiones"),
 ("p", "Puedes repetir el bloque `provider` con un nombre extra (`alias`) para trabajar en otra región:"),
 ("code", "hcl", "providers.tf", """provider "aws" {
  region = "eu-west-1"
}

provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}

resource "aws_s3_bucket" "usa" {
  provider      = aws.virginia
  bucket_prefix = "datos-us-"
}"""),
 ("p", "El bucket `usa` se crea en Virginia (us-east-1). Los recursos sin `provider` usan el primero."),
]

TEST = [
 ("¿Qué versiones acepta la restricción `~> 6.0`?",
  ["Solo la 6.0.0", "De 6.0 a 6.x, pero no 7.0", "Cualquier versión ≥ 6.0", "De 6.0.0 a 6.0.x"], 1,
  "`~>` permite que aumente solo el último número indicado (el menor, en este caso)."),
 ("¿Para qué sirve `.terraform.lock.hcl`?",
  ["Para bloquear el estado", "Para fijar la versión exacta y los hashes de los providers", "Para guardar contraseñas", "Para impedir el destroy"], 1,
  "Garantiza que todos instalan exactamente la misma versión. Se sube a Git."),
 ("¿Cuál es la forma CORRECTA de dar credenciales de AWS a Terraform?",
  ["Escribir access_key en el provider", "Un perfil de AWS (AWS_PROFILE) o variables de entorno", "Ponerlas en terraform.tfvars y subirlo", "En un comentario"], 1,
  "Las credenciales deben vivir fuera del código: perfiles, SSO, variables de entorno o roles."),
 ("Has cambiado `version = \"~> 5.0\"` por `\"~> 6.0\"`. `terraform init` falla. ¿Qué haces?",
  ["Borrar el estado", "terraform init -upgrade", "terraform apply", "Reinstalar Terraform"], 1,
  "El lock file aún apunta a la 5.x; `-upgrade` permite elegir una versión nueva."),
 ("¿Por qué usamos `bucket_prefix` en lugar de `bucket`?",
  ["Es obligatorio", "Porque los nombres de bucket son globales y así evitamos conflictos", "Para que sea privado", "Para que sea más barato"], 1,
  "AWS genera un sufijo único para que no choque con buckets de otras personas."),
 ("¿Cómo indicas que un recurso use el provider con `alias = \"virginia\"`?",
  ["region = \"virginia\"", "provider = aws.virginia", "alias = \"virginia\"", "provider = \"virginia\""], 1,
  "El meta-argumento `provider` recibe `NOMBRE.ALIAS` sin comillas."),
]

RETOS = [
 {"titulo": "Bucket con cifrado y bloqueo de acceso público",
  "enunciado": "Amplía el ejemplo del bucket añadiendo cifrado por defecto (SSE-S3, AES256) y el bloqueo de acceso público completo. Busca los recursos en la documentación del provider AWS.",
  "pista": "Busca `aws_s3_bucket_server_side_encryption_configuration` y `aws_s3_bucket_public_access_block`.",
  "solucion": ("hcl", """resource "aws_s3_bucket_server_side_encryption_configuration" "demo" {
  bucket = aws_s3_bucket.demo.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "demo" {
  bucket                  = aws_s3_bucket.demo.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}""")},
 {"titulo": "Mismo código, dos regiones",
  "enunciado": "Crea un bucket en `eu-west-1` y otro en `eu-central-1` usando alias. Saca ambos nombres y sus regiones (atributo `region` del bucket) como outputs.",
  "pista": "Declara un segundo provider con alias y usa `provider = aws.ALIAS` en el segundo bucket.",
  "solucion": ("hcl", """provider "aws" {
  region = "eu-west-1"
}

provider "aws" {
  alias  = "frankfurt"
  region = "eu-central-1"
}

resource "aws_s3_bucket" "irlanda" {
  bucket_prefix = "curso-ie-"
  force_destroy = true
}

resource "aws_s3_bucket" "frankfurt" {
  provider      = aws.frankfurt
  bucket_prefix = "curso-de-"
  force_destroy = true
}

output "buckets" {
  value = {
    (aws_s3_bucket.irlanda.bucket)   = aws_s3_bucket.irlanda.region
    (aws_s3_bucket.frankfurt.bucket) = aws_s3_bucket.frankfurt.region
  }
}""")},
]
