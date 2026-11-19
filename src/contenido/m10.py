# -*- coding: utf-8 -*-
# Módulo 10 · Backends remotos, bloqueo y workspaces

LECCION = [
 ("h", "El problema del estado local"),
 ("p", "Hasta ahora el estado vivía en tu ordenador. Eso tiene problemas serios en cuanto trabajas con más gente (o con un sistema de CI):"),
 ("ul", [
  "**Compartir**: tu compañera no tiene tu `terraform.tfstate`, así que para su Terraform la infraestructura no existe.",
  "**Concurrencia**: si dos personas hacen `apply` a la vez sobre el mismo estado, lo corrompen.",
  "**Pérdida**: si se rompe tu disco, pierdes el estado.",
  "**Seguridad**: el estado tiene secretos y está en un portátil sin cifrar.",
 ]),
 ("p", "La solución es un **backend remoto**: un lugar compartido donde guardar el estado, con **bloqueo** (*locking*) para que solo una operación pueda modificarlo a la vez."),
 ("table", ["Backend", "Dónde guarda el estado", "Bloqueo"], [
  ["`local`", "Archivo en disco (por defecto)", "Solo en tu máquina"],
  ["`s3`", "Bucket de Amazon S3", "Archivo `.tflock` en S3 (`use_lockfile`)"],
  ["`azurerm`", "Azure Blob Storage", "Lease del blob"],
  ["`gcs`", "Google Cloud Storage", "Nativo"],
  ["HCP Terraform (`cloud`)", "Servicio de HashiCorp", "Nativo + ejecuciones remotas"],
 ]),

 ("h", "Paso 1: crear el bucket del estado (bootstrap)"),
 ("p", "Hay un problema del huevo y la gallina: necesitas un bucket para guardar el estado, pero quieres crear ese bucket con Terraform. La solución habitual es una pequeña configuración **bootstrap** con estado local, que se ejecuta una sola vez:"),
 ("code", "hcl", "bootstrap/main.tf", """terraform {
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

data "aws_caller_identity" "actual" {}

resource "aws_s3_bucket" "estado" {
  # incluir el ID de cuenta ayuda a que el nombre sea único
  bucket = "tfstate-${data.aws_caller_identity.actual.account_id}-eu-west-1"

  lifecycle {
    prevent_destroy = true # ¡nunca borrar el estado por accidente!
  }
}

resource "aws_s3_bucket_versioning" "estado" {
  bucket = aws_s3_bucket.estado.id
  versioning_configuration {
    status = "Enabled" # permite recuperar versiones anteriores del estado
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "estado" {
  bucket = aws_s3_bucket.estado.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "estado" {
  bucket                  = aws_s3_bucket.estado.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "bucket_estado" {
  value = aws_s3_bucket.estado.bucket
}"""),
 ("code", "bash", "terminal", """cd bootstrap
terraform init && terraform apply
terraform output -raw bucket_estado
# tfstate-123456789012-eu-west-1"""),

 ("h", "Paso 2: configurar el backend S3"),
 ("p", "En tu proyecto, añade un bloque `backend` dentro de `terraform {}`:"),
 ("code", "hcl", "backend.tf", """terraform {
  backend "s3" {
    bucket       = "tfstate-123456789012-eu-west-1"
    key          = "curso/web/terraform.tfstate"  # ruta dentro del bucket
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true   # bloqueo nativo en S3 (Terraform >= 1.10)
  }
}"""),
 ("ul", [
  "`key` es la ruta del archivo dentro del bucket. Usa una por proyecto y entorno: `red/prod/terraform.tfstate`, `web/dev/terraform.tfstate`…",
  "`use_lockfile = true` crea un archivo `terraform.tfstate.tflock` mientras alguien está operando.",
 ]),
 ("info", "Antes de Terraform 1.10, el bloqueo en S3 requería una tabla de **DynamoDB** (`dynamodb_table = \"...\"`). Lo verás en muchos tutoriales y proyectos existentes; hoy está obsoleto en favor de `use_lockfile`."),
 ("warn", "Dentro del bloque `backend` **no se pueden usar variables** (`var.x`) ni locals: se evalúa antes que todo lo demás."),

 ("h", "Paso 3: migrar el estado"),
 ("p", "Al cambiar de backend hay que volver a ejecutar `init`. Terraform detecta que ya tienes un estado local y te ofrece copiarlo:"),
 ("term", """$ terraform init -migrate-state

Initializing the backend...
Do you want to copy existing state to the new backend?
  Pre-existing state was found while migrating the previous "local" backend to the
  newly configured "s3" backend. No existing state was found in the newly
  configured "s3" backend. Do you want to copy this state to the new "s3"
  backend? Enter "yes" to copy and "no" to start with an empty state.

  Enter a value: yes

Successfully configured the backend "s3"! Terraform will automatically
use this backend unless the backend configuration changes."""),
 ("p", "Comprueba que funcionó: `terraform plan` debe decir *No changes* y el estado ya está en S3:"),
 ("code", "bash", "terminal", """aws s3 ls s3://tfstate-123456789012-eu-west-1/curso/web/
# 2026-11-19 11:02:10      4521 terraform.tfstate
rm terraform.tfstate terraform.tfstate.backup   # ya no hacen falta en local"""),

 ("h", "El bloqueo en acción"),
 ("p", "Abre dos terminales en la misma carpeta y lanza `terraform apply` en ambas. La segunda verá:"),
 ("term", """╷
│ Error: Error acquiring the state lock
│
│ Error message: operation error S3: PutObject, ... PreconditionFailed
│ Lock Info:
│   ID:        a1b2c3d4-e5f6-7890-abcd-ef1234567890
│   Path:      tfstate-123456789012-eu-west-1/curso/web/terraform.tfstate
│   Operation: OperationTypeApply
│   Who:       ana@portatil
│   Version:   1.10.5
│   Created:   2026-11-19 11:05:31 UTC
│
│ Terraform acquires a state lock to protect the state from being written
│ by multiple users at the same time.
╵"""),
 ("p", "Esa protección evita corromper el estado. Si un proceso murió a medias (se cerró el portátil, se cayó el CI) y el bloqueo quedó atascado, puedes liberarlo:"),
 ("code", "bash", "terminal", """terraform force-unlock a1b2c3d4-e5f6-7890-abcd-ef1234567890
# o esperar en vez de fallar:
terraform apply -lock-timeout=5m"""),
 ("warn", "Antes de `force-unlock`, **asegúrate** de que nadie está aplicando de verdad. Si lo liberas mientras otra persona aplica, podéis corromper el estado."),

 ("h", "Configuración parcial del backend"),
 ("p", "Como no se pueden usar variables en el backend, para reutilizar el mismo código en varios entornos se usa **configuración parcial**: dejas el bloque casi vacío y pasas el resto en `init`:"),
 ("code", "hcl", "backend.tf", """terraform {
  backend "s3" {}
}"""),
 ("code", "hcl", "dev.s3.tfbackend", """bucket       = "tfstate-123456789012-eu-west-1"
key          = "web/dev/terraform.tfstate"
region       = "eu-west-1"
encrypt      = true
use_lockfile = true"""),
 ("code", "bash", "terminal", """terraform init -backend-config=dev.s3.tfbackend
# cambiar a prod (otro estado):
terraform init -reconfigure -backend-config=prod.s3.tfbackend"""),

 ("h", "Leer outputs de otro proyecto"),
 ("p", "En proyectos grandes, la infraestructura se divide en varias configuraciones (red, bases de datos, aplicaciones), cada una con su estado. Una puede leer los outputs de otra con el data source `terraform_remote_state`:"),
 ("code", "hcl", "app/main.tf", """data "terraform_remote_state" "red" {
  backend = "s3"
  config = {
    bucket = "tfstate-123456789012-eu-west-1"
    key    = "red/prod/terraform.tfstate"
    region = "eu-west-1"
  }
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"
  subnet_id     = data.terraform_remote_state.red.outputs.subred_privada_id
}"""),
 ("tip", "Alternativa con menos acoplamiento: usar data sources normales que busquen por etiquetas (`data \"aws_subnet\"` con `filter`), o guardar valores en SSM Parameter Store."),

 ("h", "Workspaces"),
 ("p", "Los **workspaces** permiten tener **varios estados con el mismo código** en el mismo backend. Siempre existe uno llamado `default`:"),
 ("code", "bash", "terminal", """terraform workspace list          # * default
terraform workspace new dev       # crea y cambia a dev
terraform workspace new prod
terraform workspace select dev
terraform workspace show          # dev"""),
 ("p", "Dentro del código, `terraform.workspace` devuelve el nombre del workspace actual:"),
 ("code", "hcl", "main.tf", """locals {
  entorno = terraform.workspace
  tamanos = {
    dev  = "t3.micro"
    prod = "t3.medium"
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = lookup(local.tamanos, local.entorno, "t3.micro")
  tags          = { Name = "web-${local.entorno}" }
}"""),
 ("p", "En S3, los estados de cada workspace se guardan en `env:/NOMBRE/<key>`."),
 ("table", ["", "Workspaces", "Una carpeta por entorno"], [
  ["Código", "Idéntico para todos", "Puede diferir (o compartir módulos)"],
  ["Riesgo", "Fácil equivocarse de workspace y aplicar en prod", "Es explícito: `cd envs/prod`"],
  ["Diferencias entre entornos", "Con condicionales y `lookup`", "Con archivos `.tfvars`/código distinto"],
  ["Ideal para", "Entornos efímeros idénticos (una rama, una demo)", "dev / staging / prod con diferencias reales"],
 ]),
 ("info", "Para entornos tipo dev/prod, la mayoría de equipos prefiere **carpetas por entorno** que reutilizan módulos (módulos 11 y 14). Los workspaces CLI brillan para copias temporales idénticas."),

 ("h", "HCP Terraform"),
 ("p", "**HCP Terraform** (antes Terraform Cloud) es el servicio de HashiCorp que, además de guardar el estado, ejecuta los `plan` y `apply` en sus servidores, guarda variables y secretos, se integra con GitHub y permite aprobar cambios desde la web. Tiene un plan gratuito limitado."),
 ("code", "hcl", "versions.tf", """terraform {
  cloud {
    organization = "mi-organizacion"
    workspaces {
      name = "curso-web-dev"
    }
  }
}"""),
 ("code", "bash", "terminal", """terraform login   # abre el navegador para obtener un token
terraform init    # conecta con HCP Terraform
terraform plan    # se ejecuta en remoto; ves la salida en tu terminal"""),
 ("p", "Alternativas al estilo de HCP Terraform: Spacelift, env0, Scalr o el open source Atlantis."),
]

TEST = [
 ("¿Qué problema resuelve el bloqueo (locking) del estado?",
  ["Que el estado sea legible", "Que dos operaciones modifiquen el estado a la vez", "Que se borren recursos", "Que el estado sea grande"], 1,
  "Solo una operación puede escribir el estado a la vez."),
 ("Con Terraform 1.10+, ¿cómo se activa el bloqueo en el backend S3?",
  ["dynamodb_table = \"locks\"", "use_lockfile = true", "lock = \"s3\"", "Viene siempre activado"], 1,
  "`use_lockfile` usa un archivo .tflock en el propio bucket. DynamoDB es el método antiguo."),
 ("¿Por qué el bucket del estado debe tener versionado?",
  ["Para que sea más barato", "Para poder recuperar versiones anteriores si el estado se corrompe", "Es obligatorio en S3", "Para el bloqueo"], 1,
  "El versionado es tu copia de seguridad del estado."),
 ("Has añadido un bloque backend a un proyecto con estado local. ¿Qué comando ejecutas?",
  ["terraform apply", "terraform init -migrate-state", "terraform state push", "terraform workspace new"], 1,
  "Copia el estado local al nuevo backend."),
 ("¿Puedes usar `var.region` dentro del bloque backend?",
  ["Sí", "No; se usa configuración parcial con -backend-config", "Solo con locals", "Solo en S3"], 1,
  "El backend se configura antes de evaluar variables."),
 ("¿Qué devuelve `terraform.workspace`?",
  ["La carpeta actual", "El nombre del workspace seleccionado", "La región", "El nombre del bucket"], 1,
  "Útil para nombrar recursos o elegir tamaños según el workspace."),
 ("Un apply en CI se cortó y el estado quedó bloqueado. Nadie más está aplicando. ¿Qué haces?",
  ["Borrar el bucket", "terraform force-unlock ID", "terraform destroy", "terraform init -upgrade"], 1,
  "Libera el bloqueo usando el ID que aparece en el mensaje de error."),
]

RETOS = [
 {"titulo": "Estado remoto completo",
  "enunciado": "Aplica el bootstrap, migra el proyecto del módulo 6 a S3 con `use_lockfile`, verifica en S3 que existe el archivo y prueba el bloqueo con dos terminales.",
  "pista": "Mientras dure el apply de la primera terminal, verás un archivo `.tflock` junto al estado con `aws s3 ls`.",
  "solucion": ("bash", """cd bootstrap && terraform init && terraform apply && cd ..
# añade backend.tf con bucket/key/region/use_lockfile
terraform init -migrate-state
aws s3 ls s3://BUCKET/curso/web/
# terminal 1: terraform apply  (no respondas al prompt todavía)
# terminal 2: terraform plan   → Error acquiring the state lock
aws s3 ls s3://BUCKET/curso/web/   # terraform.tfstate y terraform.tfstate.tflock""")},
 {"titulo": "Dos entornos con workspaces",
  "enunciado": "Usando `local_file`, crea una configuración que genere `config-<workspace>.txt` con un número de réplicas distinto en `dev` (1) y `prod` (3). Crea ambos workspaces y aplica en cada uno. ¿Cuántos archivos hay al final?",
  "pista": "Cada workspace tiene su propio estado, así que los archivos no se pisan.",
  "solucion": ("hcl", """locals {
  replicas = { dev = 1, prod = 3 }
}

resource "local_file" "config" {
  filename = "${path.module}/config-${terraform.workspace}.txt"
  content  = "replicas=${lookup(local.replicas, terraform.workspace, 1)}\\n"
}

# terraform workspace new dev  && terraform apply
# terraform workspace new prod && terraform apply
# → config-dev.txt y config-prod.txt (2 archivos, 2 estados)""")},
]
