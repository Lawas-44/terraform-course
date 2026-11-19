# -*- coding: utf-8 -*-
# Módulo 05 · Providers y conexión con la nube

LECCION = [
 ("h", "Qué es un provider"),
 ("p", "Terraform Core no sabe nada de AWS, Azure ni GitHub. Todo ese conocimiento vive en los **providers**: plugins que traducen tus bloques `resource` a llamadas a la API correspondiente. Hay más de 4.000 en el **Terraform Registry** (registry.terraform.io), clasificados en tres niveles:"),
 ("table", ["Nivel", "Quién lo mantiene", "Ejemplos"], [
  ["Official", "HashiCorp", "aws, azurerm, google, kubernetes, random, local"],
  ["Partner", "La empresa del servicio", "cloudflare, datadog, mongodbatlas"],
  ["Community", "Personas de la comunidad", "Muchos útiles; revisa su mantenimiento"],
 ]),
 ("p", "La documentación de cada provider en el Registry es **la referencia que más vas a consultar**. Para cada recurso encontrarás un ejemplo, los argumentos (*Argument Reference*), los atributos que exporta (*Attribute Reference*) y cómo importarlo (*Import*)."),

 ("h", "Declarar providers y versiones"),
 ("p", "Los providers se declaran en `required_providers` con una dirección (`source`) y una restricción de versión:"),
 ("code", "hcl", "versions.tf", """terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"   # registry.terraform.io/hashicorp/aws
      version = "~> 6.0"
    }
  }
}"""),
 ("table", ["Restricción", "Significado", "Acepta"], [
  ["`= 6.2.0`", "Exactamente esa", "6.2.0"],
  ["`>= 6.0`", "Esa o superior", "6.0, 6.5, 7.0, 8.1…"],
  ["`~> 6.0`", "Solo cambia el último número indicado", "6.0 … 6.99 (no 7.0)"],
  ["`~> 6.2.0`", "Solo parches", "6.2.0 … 6.2.x"],
  ["`>= 6.0, < 7.0`", "Rango explícito", "igual que `~> 6.0`"],
 ]),
 ("tip", "En proyectos usa `~> MAYOR.MENOR` para recibir mejoras sin cambios incompatibles. Las versiones mayores (6 → 7) suelen romper cosas y conviene actualizarlas a propósito."),

 ("h", "El lock file"),
 ("p", "Al hacer `init`, Terraform elige la versión más alta que cumpla la restricción y la apunta, con sus hashes, en `.terraform.lock.hcl`:"),
 ("code", "hcl", ".terraform.lock.hcl", """provider "registry.terraform.io/hashicorp/aws" {
  version     = "6.4.0"
  constraints = "~> 6.0"
  hashes = [
    "h1:abc123...",
    "zh:def456...",
  ]
}"""),
 ("p", "Mientras el lock file exista, `init` siempre instalará **esa misma versión**, aunque salgan otras nuevas. Así todo el equipo y el CI usan exactamente lo mismo. Por eso se sube a Git. Para actualizar a propósito:"),
 ("code", "bash", "terminal", """terraform init -upgrade   # sube a la versión más alta permitida y actualiza el lock

# Si el equipo usa varios sistemas operativos, añade hashes para todos:
terraform providers lock \\
  -platform=linux_amd64 -platform=darwin_arm64 -platform=windows_amd64"""),

 ("h", "Configurar el provider de AWS"),
 ("p", "El bloque `provider` configura cómo conectarse. Para AWS lo mínimo es la región:"),
 ("code", "hcl", "providers.tf", """provider "aws" {
  region = "eu-west-1"   # Irlanda. Otras: eu-south-2 (España), us-east-1...

  default_tags {
    tags = {
      Gestion = "terraform"
      Curso   = "terraform-desde-cero"
    }
  }
}"""),
 ("p", "`default_tags` añade esas etiquetas a **todos** los recursos que lo admitan. Así en la consola de AWS (y en la factura) sabrás qué creó Terraform."),

 ("h", "Autenticación: nunca claves en el código"),
 ("p", "El provider de AWS busca credenciales en este orden, igual que la AWS CLI:"),
 ("ol", [
  "Argumentos del bloque provider (`access_key`, `secret_key`) — **no los uses nunca**.",
  "Variables de entorno: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`.",
  "Perfil de `~/.aws/config` y `~/.aws/credentials` (el indicado en `AWS_PROFILE` o `profile`).",
  "Rol de la máquina o contenedor (EC2 instance profile, ECS, OIDC en CI…).",
 ]),
 ("code", "bash", "la forma recomendada", """export AWS_PROFILE=curso-terraform   # el perfil del módulo 1
aws sts get-caller-identity          # comprueba
terraform plan                       # Terraform usa el mismo perfil"""),
 ("warn", "Si escribes `access_key = \"AKIA...\"` en un `.tf` y lo subes a GitHub, en minutos habrá bots usando tu cuenta para minar criptomonedas. No es una exageración."),

 ("h", "Tu primer recurso en la nube: un bucket S3"),
 ("p", "S3 es el almacenamiento de objetos de AWS. Un bucket es gratuito mientras esté vacío (y casi gratuito con pocos datos). Crea una carpeta nueva con estos archivos:"),
 ("code", "hcl", "main.tf", """resource "aws_s3_bucket" "demo" {
  # Los nombres de bucket son GLOBALES (únicos en todo AWS).
  # bucket_prefix añade un sufijo aleatorio para evitar choques.
  bucket_prefix = "curso-tf-demo-"
  force_destroy = true # permite borrarlo aunque tenga archivos (solo para labs)
}

resource "aws_s3_bucket_versioning" "demo" {
  bucket = aws_s3_bucket.demo.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_object" "hola" {
  bucket       = aws_s3_bucket.demo.id
  key          = "hola.txt"
  content      = "Subido con Terraform"
  content_type = "text/plain"
}

output "bucket" {
  value = aws_s3_bucket.demo.bucket
}

output "arn" {
  value = aws_s3_bucket.demo.arn
}"""),
 ("term", """$ terraform init
$ terraform apply
...
Plan: 3 to add, 0 to change, 0 to destroy.
...
Apply complete! Resources: 3 added, 0 changed, 0 destroyed.

Outputs:
arn    = "arn:aws:s3:::curso-tf-demo-20261119103512345600000001"
bucket = "curso-tf-demo-20261119103512345600000001"

$ aws s3 ls s3://$(terraform output -raw bucket)
2026-11-19 10:35:14         20 hola.txt"""),
 ("info", "En el provider AWS moderno, la configuración del bucket (versionado, cifrado, políticas, web…) se hace con **recursos separados** como `aws_s3_bucket_versioning`, no con bloques dentro de `aws_s3_bucket`. Lo verás en tutoriales antiguos de la otra forma."),
 ("p", "Abre la consola de AWS → S3 y busca tu bucket. Mira la pestaña *Properties*: verás el versionado activado y las etiquetas de `default_tags`. Cuando termines: `terraform destroy`."),

 ("h", "Varias regiones o cuentas: alias"),
 ("p", "Puedes declarar el mismo provider varias veces con un `alias` y elegir cuál usa cada recurso con el meta-argumento `provider`:"),
 ("code", "hcl", "providers.tf", """provider "aws" {
  region = "eu-west-1"            # el de por defecto (sin alias)
}

provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}

resource "aws_s3_bucket" "europa" {
  bucket_prefix = "datos-eu-"
}

resource "aws_s3_bucket" "usa" {
  provider      = aws.virginia
  bucket_prefix = "datos-us-"
}"""),
 ("p", "Casos típicos: certificados para CloudFront (deben estar en us-east-1), réplicas de backups en otra región o gestionar varias cuentas a la vez (con `assume_role`)."),
 ("info", "Novedad del provider AWS 6.x: muchos recursos aceptan directamente un argumento `region = \"us-east-1\"`, así que para el caso «misma cuenta, otra región» ya no siempre hace falta un alias. Para otra cuenta (`assume_role`) los alias siguen siendo necesarios."),

 ("h", "Otros providers para practicar"),
 ("p", "El flujo es idéntico con cualquier provider. Algunos interesantes para practicar sin AWS:"),
 ("code", "hcl", "docker (necesita Docker instalado)", """terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

resource "docker_image" "nginx" {
  name = "nginx:alpine"
}

resource "docker_container" "web" {
  name  = "web-terraform"
  image = docker_image.nginx.image_id

  ports {
    internal = 80
    external = 8080
  }
}
# terraform apply y abre http://localhost:8080"""),
 ("p", "Otros: `integrations/github` (repositorios y equipos), `hashicorp/kubernetes`, `hashicorp/azurerm`, `hashicorp/google`, `cloudflare/cloudflare`."),
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
