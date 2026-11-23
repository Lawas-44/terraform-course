# -*- coding: utf-8 -*-
# Módulo 10 · Backends remotos, bloqueo y workspaces

LECCION = [
 ("h", "El problema del estado en tu ordenador"),
 ("p", "Hasta ahora el estado estaba en tu ordenador. Si trabajas con más personas, eso da problemas:"),
 ("ul", [
  "Tus compañeros no tienen tu archivo, así que su Terraform no sabe lo que has creado.",
  "Si dos personas aplican cambios a la vez, el estado se puede estropear.",
  "Si se rompe tu ordenador, pierdes el estado.",
 ]),
 ("p", "La solución es guardar el estado en un sitio compartido. A ese sitio se le llama **backend**. En AWS lo normal es usar un bucket de S3."),

 ("h", "Paso 1: crear el bucket para el estado"),
 ("p", "Primero creamos el bucket con un proyecto pequeño aparte (llamado *bootstrap*), que solo se ejecuta una vez:"),
 ("code", "hcl", "bootstrap/main.tf", """provider "aws" {
  region = "eu-west-1"
}

data "aws_caller_identity" "actual" {}

resource "aws_s3_bucket" "estado" {
  bucket = "tfstate-${data.aws_caller_identity.actual.account_id}"

  lifecycle {
    prevent_destroy = true   # que nadie lo borre por error
  }
}

# Guardar versiones anteriores del estado, por si algo sale mal
resource "aws_s3_bucket_versioning" "estado" {
  bucket = aws_s3_bucket.estado.id
  versioning_configuration {
    status = "Enabled"
  }
}

output "bucket_estado" {
  value = aws_s3_bucket.estado.bucket
}"""),
 ("term", """$ cd bootstrap
$ terraform init
$ terraform apply
$ terraform output -raw bucket_estado
tfstate-123456789012"""),

 ("h", "Paso 2: decirle a Terraform dónde guardar el estado"),
 ("p", "En tu proyecto, añade un bloque `backend` dentro de `terraform`:"),
 ("code", "hcl", "backend.tf", """terraform {
  backend "s3" {
    bucket       = "tfstate-123456789012"
    key          = "curso/web/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true
  }
}"""),
 ("ul", [
  "`key`: la ruta del archivo dentro del bucket. Usa una distinta para cada proyecto.",
  "`encrypt`: guarda el estado cifrado.",
  "`use_lockfile`: activa el **bloqueo** (lo vemos abajo). Necesita Terraform 1.10 o superior.",
 ]),
 ("warn", "Dentro del bloque `backend` no se pueden usar variables (`var.algo`). Si necesitas valores distintos (por ejemplo, uno por entorno), se pasan al ejecutar `terraform init -backend-config=archivo`."),

 ("h", "Paso 3: mover el estado"),
 ("p", "Ejecuta `init` otra vez. Terraform te pregunta si quieres copiar tu estado al bucket. Responde `yes`:"),
 ("term", """$ terraform init -migrate-state
Do you want to copy existing state to the new backend?
  Enter a value: yes

Successfully configured the backend "s3"!"""),
 ("p", "Desde ahora el estado vive en S3 y todo el equipo usa el mismo."),

 ("h", "El bloqueo"),
 ("p", "Mientras alguien está aplicando cambios, Terraform **bloquea** el estado. Si otra persona lo intenta a la vez, recibe este mensaje y tiene que esperar:"),
 ("term", """$ terraform apply
Error: Error acquiring the state lock

Lock Info:
  ID:        a1b2c3d4-e5f6-7890-abcd-ef1234567890
  Who:       ana@portatil
  Operation: OperationTypeApply"""),
 ("p", "Si un proceso se cortó y el bloqueo se quedó puesto, se puede quitar con el ID del mensaje:"),
 ("term", """$ terraform force-unlock a1b2c3d4-e5f6-7890-abcd-ef1234567890"""),
 ("warn", "Antes de quitar un bloqueo, asegúrate de que nadie está aplicando cambios en ese momento."),
 ("info", "En tutoriales antiguos verás que el bloqueo se hacía con una tabla de DynamoDB. Hoy basta con `use_lockfile = true`."),

 ("h", "Varios entornos con el mismo código: workspaces"),
 ("p", "Un **workspace** es un estado separado que usa el mismo código. Sirve para tener, por ejemplo, un entorno `dev` y otro `prod` sin que se mezclen:"),
 ("term", """$ terraform workspace new dev
$ terraform workspace new prod
$ terraform workspace select dev
$ terraform workspace list
  default
* dev
  prod"""),
 ("p", "En el código, `terraform.workspace` te dice en qué workspace estás:"),
 ("code", "hcl", "main.tf", """resource "local_file" "config" {
  filename = "config-${terraform.workspace}.txt"
  content  = "entorno=${terraform.workspace}"
}"""),
 ("tip", "Muchos equipos prefieren usar una carpeta por entorno (`envs/dev`, `envs/prod`) en lugar de workspaces, porque así es más difícil equivocarse de entorno. Lo verás en el módulo 14."),

 ("h", "HCP Terraform"),
 ("p", "**HCP Terraform** es un servicio de HashiCorp (la empresa de Terraform) que guarda el estado por ti y además ejecuta los comandos en sus servidores. Tiene un plan gratuito. Para conectarte se usa `terraform login`."),
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


PROYECTO = {'titulo': 'Guarda el estado en S3',
 'bloques': [('p',
              'Vas a guardar el estado del proyecto en un bucket de S3. Así no lo pierdes si cambias de '
              'ordenador, y GitHub Actions podrá usarlo.'),
             ('p',
              '1. Crea el bucket con el bootstrap de la lección (está en `labs/10-backend-s3/bootstrap` del '
              'repositorio del curso). Solo se hace una vez:'),
             ('term',
              '$ cd labs/10-backend-s3/bootstrap\n'
              '$ terraform init && terraform apply\n'
              '$ terraform output -raw bucket_estado\n'
              'tfstate-123456789012-eu-west-1'),
             ('p',
              '2. En tu proyecto, añade el backend vacío dentro del bloque `terraform` de `versions.tf`:'),
             ('code', 'hcl', 'terraform/versions.tf (añadir dentro de terraform { })', '  backend "s3" {}'),
             ('p', '3. Pon los datos en un archivo aparte (configuración parcial):'),
             ('code',
              'hcl',
              'terraform/backend.hcl',
              'bucket       = "tfstate-123456789012-eu-west-1"\n'
              'key          = "mi-web-en-la-nube/terraform.tfstate"\n'
              'region       = "eu-west-1"\n'
              'encrypt      = true\n'
              'use_lockfile = true'),
             ('p', '4. Mueve el estado:'),
             ('term',
              '$ terraform init -backend-config=backend.hcl -migrate-state\n'
              'Do you want to copy existing state to the new backend?\n'
              '  Enter a value: yes\n'
              '\n'
              'Successfully configured the backend "s3"!\n'
              '$ terraform plan\n'
              'No changes. Your infrastructure matches the configuration.\n'
              '$ rm terraform.tfstate terraform.tfstate.backup'),
             ('p', 'Sube un `backend.hcl.example` (sin tu número de cuenta) para que otros sepan qué poner.'),
             ('p',
              'Resultado de este paso: el estado del proyecto está seguro en S3, con versiones y bloqueo.')]}
