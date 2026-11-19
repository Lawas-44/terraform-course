# -*- coding: utf-8 -*-
# Datos del temario. Usa `texto` para código en línea.

MODULOS = [
{
 "num": "00", "slug": "introduccion", "titulo": "Introducción a la Infraestructura como Código",
 "nivel": "Básico", "duracion": "1 h",
 "resumen": "Qué problema resuelve Terraform, qué es la IaC y cómo encaja Terraform frente a otras herramientas.",
 "objetivos": [
  "Explicar qué es la Infraestructura como Código (IaC) y qué problemas resuelve.",
  "Diferenciar el enfoque declarativo del imperativo.",
  "Situar Terraform frente a Ansible, CloudFormation, Pulumi y OpenTofu.",
  "Entender el ciclo de vida básico: escribir → planificar → aplicar → destruir.",
 ],
 "temas": [
  "El problema de la infraestructura manual: «ClickOps», errores humanos, entornos que no se parecen entre sí, falta de historial.",
  "Qué es la IaC: la infraestructura descrita en archivos de texto, versionada en Git y revisable como cualquier código.",
  "Declarativo (describes el estado final) vs imperativo (describes los pasos). Idempotencia.",
  "Herramientas de aprovisionamiento (Terraform, CloudFormation, Pulumi) vs gestión de configuración (Ansible, Chef, Puppet).",
  "Terraform y OpenTofu: cambio de licencia (BSL, 2023), el fork OpenTofu y por qué lo aprendido sirve para ambos.",
  "Arquitectura de Terraform: el binario (core) + providers (plugins) + estado (state).",
  "Qué es HCL y qué es el Terraform Registry.",
  "Casos de uso reales: cloud (AWS, Azure, GCP), Kubernetes, GitHub, DNS, monitorización, SaaS…",
 ],
 "ejemplo": None,
 "lab": {"titulo": "Mapa mental de la IaC",
  "pasos": [
   "Elige una infraestructura sencilla que conozcas (por ejemplo, una web con un servidor y una base de datos).",
   "Escribe los pasos manuales que harías en la consola web para crearla.",
   "Reescribe lo mismo como una lista de «cosas que deben existir» (enfoque declarativo).",
   "Anota qué pasaría si tuvieras que repetirlo en 3 entornos (dev, staging, prod).",
  ]},
 "comandos": [],
 "errores": [
  ("Pensar que Terraform sirve para instalar software dentro de servidores", "Terraform crea y gestiona recursos; la configuración interna suele hacerla otra herramienta (cloud-init, Ansible, imágenes)."),
  ("Creer que hay que aprender un lenguaje de programación", "HCL es un lenguaje de configuración sencillo; no necesitas saber programar."),
 ],
 "quiz": [
  "¿Qué significa que Terraform sea declarativo?",
  "¿Qué tres piezas componen Terraform (core, providers, …)?",
  "¿Cuál es la diferencia principal entre Terraform y Ansible?",
 ],
},
{
 "num": "01", "slug": "entorno", "titulo": "Preparación del entorno",
 "nivel": "Básico", "duracion": "1,5 h",
 "resumen": "Terminal, instalación de Terraform, editor, Git y la cuenta en la nube preparada de forma segura.",
 "objetivos": [
  "Moverse con soltura por la terminal (Linux/macOS y PowerShell).",
  "Instalar Terraform y gestionar varias versiones.",
  "Configurar VS Code con la extensión oficial de HashiCorp.",
  "Preparar Git y un repositorio para los ejercicios.",
  "Crear una cuenta en AWS con un usuario no-root, MFA y alertas de presupuesto.",
 ],
 "temas": [
  "Terminal mínima: `pwd`, `ls`, `cd`, `mkdir`, `cat`, rutas relativas/absolutas, variables de entorno.",
  "Instalar Terraform: gestor de paquetes (`brew`, `apt`, `winget`/`choco`) o binario manual; añadirlo al `PATH`.",
  "Gestores de versiones: `tfenv` o `tenv` y el archivo `.terraform-version`.",
  "VS Code + extensión «HashiCorp Terraform»: resaltado, autocompletado, formateo al guardar.",
  "Git básico y un `.gitignore` correcto para Terraform (qué nunca se sube).",
  "Cuenta AWS segura: MFA en root, usuario IAM/IAM Identity Center, AWS CLI y perfiles.",
  "Control de costes: capa gratuita, AWS Budgets, y la regla de oro «`terraform destroy` al terminar».",
  "Alternativa sin coste: Docker Desktop / provider `local` para los primeros módulos.",
 ],
 "ejemplo": ("text", ".gitignore recomendado", """# Carpeta de plugins y módulos descargados
.terraform/

# Estado: contiene datos sensibles. Nunca a Git.
*.tfstate
*.tfstate.*

# Planes guardados y logs
*.tfplan
crash.log
crash.*.log

# Variables con secretos
*.tfvars
*.tfvars.json
!example.tfvars

# Overrides locales
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# OJO: .terraform.lock.hcl SÍ se sube al repositorio"""),
 "lab": {"titulo": "Entorno listo",
  "pasos": [
   "Instala Terraform y comprueba la versión con `terraform version`.",
   "Activa el autocompletado: `terraform -install-autocomplete`.",
   "Instala la AWS CLI y ejecuta `aws configure` (o `aws configure sso`).",
   "Verifica la identidad con `aws sts get-caller-identity`.",
   "Crea un presupuesto de 5 USD con alerta por email en AWS Budgets.",
   "Crea un repositorio `terraform-labs` con el `.gitignore` anterior.",
  ]},
 "comandos": [
  ("terraform version", "Muestra la versión de Terraform y de los providers."),
  ("terraform -install-autocomplete", "Instala el autocompletado en bash/zsh."),
  ("aws sts get-caller-identity", "Comprueba con qué cuenta y usuario estás autenticado."),
  ("tfenv install 1.9.8 && tfenv use 1.9.8", "Instala y activa una versión concreta (ejemplo)."),
 ],
 "errores": [
  ("`terraform: command not found`", "El binario no está en el `PATH`. Reabre la terminal o añade la carpeta al `PATH`."),
  ("Usar la cuenta root de AWS con access keys", "Nunca. Crea un usuario/rol con permisos y activa MFA en root."),
  ("Subir `terraform.tfstate` o claves a GitHub", "Configura el `.gitignore` antes del primer commit y usa `git status` antes de cada `git add`."),
 ],
 "quiz": [
  "¿Por qué el archivo `.terraform.lock.hcl` sí se versiona y el `.tfstate` no?",
  "¿Qué comando te dice con qué identidad estás usando AWS?",
 ],
},
{
 "num": "02", "slug": "primer-proyecto", "titulo": "Tu primer proyecto: el flujo de trabajo",
 "nivel": "Básico", "duracion": "1,5 h",
 "resumen": "init → plan → apply → destroy, sin gastar un céntimo, usando providers locales.",
 "objetivos": [
  "Crear un proyecto mínimo y entender qué archivos genera Terraform.",
  "Ejecutar el flujo completo `init`, `plan`, `apply` y `destroy`.",
  "Leer e interpretar la salida de un plan (`+`, `~`, `-`, `-/+`).",
  "Entender qué es el archivo de estado y para qué sirve.",
 ],
 "temas": [
  "Estructura de carpeta: un directorio = una configuración (root module).",
  "El bloque `terraform {}` y `required_providers`.",
  "Providers sin nube: `hashicorp/local` y `hashicorp/random`.",
  "`terraform init`: descarga providers, crea `.terraform/` y `.terraform.lock.hcl`.",
  "`terraform plan`: compara código vs estado vs realidad. Símbolos del plan.",
  "`terraform apply`: confirmación, `-auto-approve` y por qué evitarlo al aprender.",
  "`terraform.tfstate`: primer vistazo al estado.",
  "Cambiar el código y volver a planificar: actualización en sitio vs reemplazo.",
  "`terraform destroy`.",
 ],
 "ejemplo": ("hcl", "main.tf", """terraform {
  required_version = ">= 1.6"

  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

resource "random_pet" "nombre" {
  length = 2
}

resource "local_file" "saludo" {
  filename = "${path.module}/saludo.txt"
  content  = "¡Hola, ${random_pet.nombre.id}! Este archivo lo creó Terraform.\\n"
}

output "nombre_mascota" {
  value = random_pet.nombre.id
}"""),
 "lab": {"titulo": "Hola, Terraform (carpeta `labs/02-primer-proyecto`)",
  "pasos": [
   "Copia el `main.tf` de ejemplo en una carpeta nueva.",
   "Ejecuta `terraform init` y explora la carpeta `.terraform/`.",
   "Ejecuta `terraform plan` y lee cada línea del plan.",
   "Ejecuta `terraform apply` y abre `saludo.txt`.",
   "Cambia `length = 3`, vuelve a planificar y observa el reemplazo (`-/+`).",
   "Borra a mano `saludo.txt` y ejecuta `terraform plan`: Terraform detecta la diferencia.",
   "Termina con `terraform destroy`.",
  ]},
 "comandos": [
  ("terraform init", "Inicializa el directorio: descarga providers y módulos."),
  ("terraform plan", "Muestra qué cambios se harían sin aplicarlos."),
  ("terraform apply", "Aplica los cambios (pide confirmación)."),
  ("terraform destroy", "Destruye todo lo gestionado por esta configuración."),
  ("terraform output", "Muestra los outputs."),
 ],
 "errores": [
  ("`Error: Inconsistent dependency lock file`", "Has cambiado versiones de providers. Ejecuta `terraform init -upgrade`."),
  ("Ejecutar comandos fuera de la carpeta del proyecto", "Terraform trabaja sobre el directorio actual (`pwd`). Usa `cd` o `-chdir=ruta`."),
 ],
 "quiz": [
  "¿Qué significa el símbolo `-/+` en un plan?",
  "¿Qué carpeta y qué archivo crea `terraform init`?",
  "Si borras un recurso a mano, ¿qué hará el siguiente `plan`?",
 ],
},
{
 "num": "03", "slug": "hcl", "titulo": "El lenguaje HCL",
 "nivel": "Básico", "duracion": "1,5 h",
 "resumen": "Sintaxis, bloques, tipos de datos, referencias y convenciones de estilo.",
 "objetivos": [
  "Reconocer la anatomía de un bloque: tipo, etiquetas y cuerpo.",
  "Conocer los tipos de datos: string, number, bool, list, set, map, object, tuple.",
  "Usar interpolación, heredocs y referencias entre recursos.",
  "Aplicar `terraform fmt` y `terraform validate`.",
 ],
 "temas": [
  "Bloques, argumentos y atributos. Bloques de nivel superior: `terraform`, `provider`, `resource`, `data`, `variable`, `output`, `locals`, `module`.",
  "Identificadores y referencias: `TIPO.NOMBRE.ATRIBUTO`.",
  "Tipos primitivos y complejos. Conversión implícita.",
  "Strings: interpolación `${...}`, directivas `%{ if }` / `%{ for }`, heredoc `<<-EOT`.",
  "Comentarios: `#`, `//`, `/* */`.",
  "Cómo organizar archivos: `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`, `versions.tf`, `locals.tf`.",
  "Terraform carga todos los `.tf` del directorio: el orden de archivos no importa.",
  "Estilo: indentación de 2 espacios, alinear `=`, nombres en snake_case.",
 ],
 "ejemplo": ("hcl", "tipos.tf", """locals {
  texto  = "hola"
  numero = 42
  activo = true
  lista  = ["a", "b", "c"]
  mapa   = { entorno = "dev", equipo = "plataforma" }
  objeto = { nombre = "web", puertos = [80, 443] }

  mensaje = <<-EOT
    Entorno: ${local.mapa.entorno}
    Primer puerto: ${local.objeto.puertos[0]}
  EOT
}"""),
 "lab": {"titulo": "Explora tipos con la consola",
  "pasos": [
   "Pega los `locals` del ejemplo en un proyecto vacío.",
   "Abre `terraform console` y evalúa `local.lista[1]`, `local.mapa[\"equipo\"]`, `local.mensaje`.",
   "Desordena la indentación a propósito y ejecuta `terraform fmt -diff`.",
   "Introduce un error de sintaxis y lee el mensaje de `terraform validate`.",
  ]},
 "comandos": [
  ("terraform fmt", "Formatea los .tf del directorio actual."),
  ("terraform fmt -recursive -diff", "Formatea subcarpetas y muestra los cambios."),
  ("terraform fmt -check", "Falla si algo no está formateado (útil en CI)."),
  ("terraform validate", "Valida sintaxis y coherencia interna."),
  ("terraform console", "Consola interactiva para probar expresiones."),
 ],
 "errores": [
  ("`Error: Unsupported argument`", "Argumento mal escrito o que no existe en ese recurso. Revisa la documentación del provider."),
  ("Usar comillas simples `'texto'`", "HCL solo acepta comillas dobles."),
 ],
 "quiz": [
  "¿Diferencia entre `list` y `set`?",
  "¿En qué orden lee Terraform los archivos .tf?",
 ],
},
{
 "num": "04", "slug": "variables-outputs-locals", "titulo": "Variables, outputs y locals",
 "nivel": "Básico", "duracion": "2 h",
 "resumen": "Parametrizar configuraciones, exponer resultados y evitar repetición.",
 "objetivos": [
  "Declarar variables con tipo, descripción, valor por defecto y validación.",
  "Conocer todas las formas de asignar valores y su orden de precedencia.",
  "Exponer datos con outputs y consumirlos desde la terminal.",
  "Usar `locals` para nombres y etiquetas comunes.",
  "Marcar valores como `sensitive` y saber sus limitaciones.",
 ],
 "temas": [
  "Bloque `variable`: `type`, `default`, `description`, `nullable`, `sensitive`, `validation`.",
  "Asignar valores: `-var`, `-var-file`, `terraform.tfvars`, `*.auto.tfvars`, variables de entorno `TF_VAR_nombre`, prompt interactivo.",
  "Precedencia (de menor a mayor): entorno → `terraform.tfvars` → `*.auto.tfvars` (orden alfabético) → `-var`/`-var-file` (en el orden escrito).",
  "Tipos complejos en variables: `list(string)`, `map(string)`, `object({...})`, `optional()`.",
  "Bloque `output`: `value`, `description`, `sensitive`. `terraform output -json` + `jq`.",
  "`locals`: valores calculados y reutilizables; cuándo usar local vs variable.",
  "`sensitive = true` oculta el valor en pantalla, pero **sigue guardado en el estado**.",
 ],
 "ejemplo": ("hcl", "variables.tf", """variable "entorno" {
  description = "Nombre del entorno (dev, staging o prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.entorno)
    error_message = "El entorno debe ser dev, staging o prod."
  }
}

variable "proyecto" {
  type = string
}

locals {
  prefijo = "${var.proyecto}-${var.entorno}"
  etiquetas = {
    Proyecto = var.proyecto
    Entorno  = var.entorno
    Gestion  = "terraform"
  }
}

output "prefijo" {
  description = "Prefijo usado en los nombres de recursos"
  value       = local.prefijo
}"""),
 "lab": {"titulo": "Parametriza el proyecto del módulo 2",
  "pasos": [
   "Convierte el nombre del archivo y el contenido en variables.",
   "Crea `dev.tfvars` y `prod.tfvars` y aplica con `-var-file`.",
   "Prueba a dar un valor no permitido y observa la validación.",
   "Exporta `TF_VAR_proyecto=demo` y comprueba la precedencia.",
   "Saca un output en JSON y fíltralo con `jq`.",
  ]},
 "comandos": [
  ("terraform plan -var=\"entorno=prod\"", "Asigna una variable desde la línea de comandos."),
  ("terraform apply -var-file=\"prod.tfvars\"", "Carga variables desde un archivo."),
  ("export TF_VAR_proyecto=demo", "Asigna una variable vía entorno (bash)."),
  ("$env:TF_VAR_proyecto = \"demo\"", "Lo mismo en PowerShell."),
  ("terraform output -json | jq", "Outputs en JSON formateado."),
  ("terraform output -raw prefijo", "Valor sin comillas, ideal para scripts."),
 ],
 "errores": [
  ("Terraform pregunta por una variable cada vez", "No tiene `default` ni valor asignado. Añádelo a `terraform.tfvars`."),
  ("Creer que `sensitive` cifra el valor", "Solo lo oculta en la salida. Protege el estado (backend cifrado, acceso restringido)."),
 ],
 "quiz": [
  "Si un valor está en `terraform.tfvars` y en `-var`, ¿cuál gana?",
  "¿Cuándo usarías `locals` en lugar de una variable?",
 ],
},
{
 "num": "05", "slug": "providers", "titulo": "Providers y conexión con la nube",
 "nivel": "Básico", "duracion": "1,5 h",
 "resumen": "Configurar el provider de AWS, versiones, lock file, alias y autenticación segura.",
 "objetivos": [
  "Configurar el provider de AWS y autenticarse sin escribir claves en el código.",
  "Entender restricciones de versión (`=`, `>=`, `~>`) y el lock file.",
  "Usar varios providers y alias (por ejemplo, dos regiones).",
  "Crear el primer recurso real en la nube (un bucket S3).",
 ],
 "temas": [
  "Qué es un provider: plugin que traduce HCL a llamadas API. Tiers: official, partner, community.",
  "Leer la documentación del Registry: argumentos, atributos exportados, import.",
  "Version constraints y `.terraform.lock.hcl`; `terraform init -upgrade`.",
  "Autenticación AWS: cadena de credenciales (variables de entorno, perfiles, SSO, roles). Nunca claves en `.tf`.",
  "`default_tags` para etiquetar todos los recursos.",
  "Alias de providers: multi-región y multi-cuenta.",
  "Otros providers útiles para practicar: `docker`, `github`, `kubernetes`, `azurerm`, `google`.",
 ],
 "ejemplo": ("hcl", "providers.tf", """terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region  = "eu-west-1"
  profile = "curso-terraform" # o usa AWS_PROFILE

  default_tags {
    tags = {
      Gestion = "terraform"
      Curso   = "terraform-desde-cero"
    }
  }
}

# Segunda región con alias
provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}

resource "aws_s3_bucket" "demo" {
  bucket_prefix = "curso-tf-demo-"
}"""),
 "lab": {"titulo": "Tu primer bucket S3",
  "pasos": [
   "Configura un perfil con `aws configure --profile curso-terraform`.",
   "Crea el bucket del ejemplo y localízalo en la consola de AWS.",
   "Revisa el contenido de `.terraform.lock.hcl`.",
   "Cambia la restricción de versión y prueba `terraform init -upgrade`.",
   "Destruye el bucket.",
  ]},
 "comandos": [
  ("terraform providers", "Lista los providers que requiere la configuración."),
  ("terraform init -upgrade", "Actualiza providers dentro de las restricciones."),
  ("terraform providers lock -platform=linux_amd64 -platform=darwin_arm64 -platform=windows_amd64", "Añade hashes para varios sistemas al lock file."),
  ("export AWS_PROFILE=curso-terraform", "Selecciona el perfil de AWS (bash)."),
 ],
 "errores": [
  ("`No valid credential sources found`", "No hay credenciales. Revisa `AWS_PROFILE` y `aws sts get-caller-identity`."),
  ("`BucketAlreadyExists`", "Los nombres de bucket son globales. Usa `bucket_prefix` o un sufijo aleatorio."),
 ],
 "quiz": [
  "¿Qué permite `~> 6.0` y qué no?",
  "¿Para qué sirve un alias de provider?",
 ],
},
{
 "num": "06", "slug": "recursos-dependencias", "titulo": "Recursos, data sources y dependencias",
 "nivel": "Básico", "duracion": "2,5 h",
 "resumen": "Construir una pequeña red y un servidor en AWS entendiendo el grafo de dependencias.",
 "objetivos": [
  "Referenciar atributos de un recurso desde otro.",
  "Distinguir `resource` (crea) de `data` (lee).",
  "Entender el grafo de dependencias y el paralelismo.",
  "Desplegar una EC2 con un servidor web accesible.",
 ],
 "temas": [
  "Anatomía de un recurso: argumentos de entrada vs atributos calculados («known after apply»).",
  "Dependencias implícitas (por referencia) y explícitas (`depends_on`).",
  "El grafo: `terraform graph` y ejecución en paralelo (`-parallelism`).",
  "Data sources: buscar la AMI más reciente, la VPC por defecto, la cuenta actual, zonas de disponibilidad.",
  "Recursos básicos de red en AWS: VPC, subnet, internet gateway, route table, security group.",
  "`user_data` para arrancar un servidor web.",
  "Recursos que se reemplazan vs se actualizan («forces replacement»).",
 ],
 "ejemplo": ("hcl", "main.tf", """data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_security_group" "web" {
  name_prefix = "web-"
  description = "Permite HTTP"
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "todo" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = <<-EOF
    #!/bin/bash
    dnf install -y nginx
    echo "Hola desde Terraform" > /usr/share/nginx/html/index.html
    systemctl enable --now nginx
  EOF

  tags = { Name = "web-curso" }
}

output "url" {
  value = "http://${aws_instance.web.public_ip}"
}"""),
 "lab": {"titulo": "Servidor web en EC2",
  "pasos": [
   "Despliega el ejemplo en la VPC por defecto y abre la URL del output.",
   "Genera el grafo con `terraform graph | dot -Tsvg > grafo.svg` y analízalo.",
   "Cambia `user_data` y observa en el plan si actualiza o reemplaza.",
   "Reto: crea tu propia VPC con una subnet pública e internet gateway.",
   "Destruye todo al terminar.",
  ]},
 "comandos": [
  ("terraform graph | dot -Tsvg > grafo.svg", "Dibuja el grafo de dependencias (requiere Graphviz)."),
  ("terraform apply -parallelism=5", "Limita las operaciones simultáneas."),
  ("terraform state list", "Lista los recursos gestionados."),
  ("terraform state show aws_instance.web", "Muestra todos los atributos de un recurso."),
 ],
 "errores": [
  ("La web no carga", "Revisa reglas del security group, IP pública y espera a que termine `user_data`."),
  ("`depends_on` en todas partes", "Úsalo solo si no hay referencia directa; las referencias ya crean la dependencia."),
 ],
 "quiz": [
  "¿Qué diferencia hay entre un `resource` y un `data`?",
  "¿Qué significa «(known after apply)»?",
 ],
},
{
 "num": "07", "slug": "meta-argumentos", "titulo": "Meta-argumentos: count, for_each y lifecycle",
 "nivel": "Intermedio", "duracion": "2 h",
 "resumen": "Crear múltiples recursos y controlar su ciclo de vida.",
 "objetivos": [
  "Crear N recursos con `count` y con `for_each`, y elegir entre ellos.",
  "Controlar el ciclo de vida con `lifecycle`.",
  "Proteger recursos críticos contra borrados accidentales.",
 ],
 "temas": [
  "Meta-argumentos disponibles en todo recurso: `count`, `for_each`, `depends_on`, `provider`, `lifecycle`.",
  "`count` + `count.index`; creación condicional con `count = var.crear ? 1 : 0`.",
  "`for_each` con map o set: `each.key`, `each.value`.",
  "Por qué `for_each` suele ser mejor: eliminar un elemento de en medio con `count` desplaza índices y recrea recursos.",
  "`lifecycle`: `create_before_destroy`, `prevent_destroy`, `ignore_changes`, `replace_triggered_by`.",
  "Forzar un reemplazo: `terraform apply -replace=DIRECCION` (sustituye al antiguo `taint`).",
 ],
 "ejemplo": ("hcl", "usuarios.tf", """variable "usuarios" {
  type    = set(string)
  default = ["ana", "luis", "marta"]
}

resource "aws_iam_user" "equipo" {
  for_each = var.usuarios
  name     = each.key
}

resource "aws_s3_bucket" "logs" {
  bucket_prefix = "logs-"

  lifecycle {
    prevent_destroy = true
    ignore_changes  = [tags["UltimaRevision"]]
  }
}"""),
 "lab": {"titulo": "count vs for_each",
  "pasos": [
   "Crea 3 archivos locales con `count` a partir de una lista.",
   "Elimina el elemento del medio y observa el plan.",
   "Repite con `for_each` y compara.",
   "Añade `prevent_destroy` a un recurso e intenta destruirlo.",
  ]},
 "comandos": [
  ("terraform apply -replace=\"aws_instance.web\"", "Fuerza la recreación de un recurso."),
  ("terraform state list 'aws_iam_user.equipo'", "Lista las instancias de un recurso con for_each."),
  ("terraform plan -target='aws_iam_user.equipo[\"ana\"]'", "Planifica solo un recurso (uso excepcional)."),
 ],
 "errores": [
  ("`The \"for_each\" value depends on resource attributes that cannot be determined until apply`", "Las claves de `for_each` deben conocerse en el plan; usa valores estáticos o variables."),
  ("Abusar de `-target`", "Es para emergencias; deja el estado desalineado con el código si se usa como rutina."),
 ],
 "quiz": [
  "¿Por qué quitar un elemento de una lista con `count` puede recrear recursos?",
  "¿Qué hace `create_before_destroy`?",
 ],
},
{
 "num": "08", "slug": "expresiones-funciones", "titulo": "Expresiones y funciones",
 "nivel": "Intermedio", "duracion": "2 h",
 "resumen": "Condicionales, bucles `for`, splat, bloques dinámicos y funciones integradas.",
 "objetivos": [
  "Escribir condicionales y expresiones `for` para transformar datos.",
  "Generar bloques anidados con `dynamic`.",
  "Usar las funciones más comunes y probarlas en `terraform console`.",
 ],
 "temas": [
  "Operadores aritméticos, de comparación y lógicos.",
  "Condicional ternario: `condicion ? a : b`.",
  "Expresiones `for` para listas `[for x in lista : upper(x)]` y mapas `{for k, v in mapa : k => v}`, con filtro `if`.",
  "Splat: `aws_instance.web[*].id`.",
  "Bloques `dynamic` (reglas, etiquetas, ajustes repetidos).",
  "Funciones: strings (`format`, `join`, `split`, `replace`, `lower`), colecciones (`length`, `merge`, `lookup`, `concat`, `flatten`, `toset`, `keys`, `values`), red (`cidrsubnet`), archivos (`file`, `templatefile`), codificación (`jsonencode`, `yamldecode`), `try`, `coalesce`.",
  "Nota: Terraform no admite funciones definidas por el usuario (salvo funciones aportadas por providers).",
 ],
 "ejemplo": ("hcl", "expresiones.tf", """locals {
  entornos = ["dev", "staging", "prod"]

  nombres = [for e in local.entornos : "app-${e}"]

  solo_prod = [for e in local.entornos : e if e == "prod"]

  subredes = {
    for i, az in ["a", "b", "c"] :
    az => cidrsubnet("10.0.0.0/16", 8, i)
  }

  tipo_instancia = var.entorno == "prod" ? "t3.medium" : "t3.micro"
}

resource "aws_security_group" "web" {
  name_prefix = "web-"

  dynamic "ingress" {
    for_each = [80, 443]
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}"""),
 "lab": {"titulo": "Juega en la consola",
  "pasos": [
   "En `terraform console` calcula 4 subredes /24 dentro de `10.0.0.0/16` con `cidrsubnet`.",
   "Convierte una lista de nombres en un mapa nombre → longitud.",
   "Genera un JSON de política IAM con `jsonencode`.",
   "Renderiza un `user_data` con `templatefile`.",
  ]},
 "comandos": [
  ("echo 'cidrsubnet(\"10.0.0.0/16\", 8, 2)' | terraform console", "Evalúa una expresión sin abrir la consola interactiva."),
  ("terraform console -var-file=dev.tfvars", "Consola con las variables cargadas."),
 ],
 "errores": [
  ("`Inconsistent conditional result types`", "Las dos ramas del ternario deben devolver el mismo tipo."),
  ("`dynamic` en exceso", "Si el código se vuelve ilegible, simplifica o separa en recursos independientes."),
 ],
 "quiz": [
  "Escribe un `for` que filtre los números pares de una lista.",
  "¿Qué devuelve `cidrsubnet(\"10.0.0.0/16\", 8, 1)`?",
 ],
},
{
 "num": "09", "slug": "estado", "titulo": "El estado (state) en profundidad",
 "nivel": "Intermedio", "duracion": "2 h",
 "resumen": "Qué guarda el estado, el drift y cómo manipularlo sin romper nada.",
 "objetivos": [
  "Explicar para qué sirve el estado y qué riesgos tiene.",
  "Detectar y corregir el drift (cambios fuera de Terraform).",
  "Usar los subcomandos de `terraform state` de forma segura.",
 ],
 "temas": [
  "Funciones del estado: mapear código ↔ recursos reales, metadatos, dependencias, rendimiento.",
  "Formato JSON del estado; `serial` y `lineage`.",
  "Datos sensibles en el estado: contraseñas, claves… en texto plano.",
  "Drift: `terraform plan -refresh-only` y `terraform apply -refresh-only`.",
  "`terraform state list | show | mv | rm | pull | push` (con precaución).",
  "Copias de seguridad: `terraform.tfstate.backup` y versionado del backend.",
  "Reglas: nunca editar el estado a mano; nunca compartirlo por email o Git.",
 ],
 "ejemplo": None,
 "lab": {"titulo": "Provoca y corrige drift",
  "pasos": [
   "Crea un bucket S3 con etiquetas desde Terraform.",
   "Modifica una etiqueta desde la consola de AWS.",
   "Ejecuta `terraform plan -refresh-only` e interpreta la salida.",
   "Decide: aceptar el cambio (`apply -refresh-only`) o revertirlo (`apply`).",
   "Renombra el recurso en el código y usa `terraform state mv` para evitar recrearlo.",
  ]},
 "comandos": [
  ("terraform show", "Muestra el estado actual de forma legible."),
  ("terraform show -json | jq", "Estado completo en JSON."),
  ("terraform plan -refresh-only", "Muestra el drift sin proponer cambios de infraestructura."),
  ("terraform state mv aws_s3_bucket.a aws_s3_bucket.b", "Renombra un recurso en el estado."),
  ("terraform state rm aws_s3_bucket.demo", "Deja de gestionar un recurso (no lo borra)."),
  ("terraform state pull > backup.tfstate", "Descarga una copia del estado (incluido remoto)."),
 ],
 "errores": [
  ("Perder el archivo de estado", "Terraform «olvida» los recursos; habrá que importarlos. Por eso se usa backend remoto con versionado."),
  ("`state rm` pensando que borra el recurso", "Solo lo quita del estado; el recurso sigue existiendo (y cobrando)."),
 ],
 "quiz": [
  "¿Qué pasa si dos personas aplican a la vez con un estado local?",
  "¿Qué diferencia hay entre `state rm` y `destroy`?",
 ],
},
{
 "num": "10", "slug": "backends-workspaces", "titulo": "Backends remotos, bloqueo y workspaces",
 "nivel": "Intermedio", "duracion": "2 h",
 "resumen": "Guardar el estado en S3 o HCP Terraform, bloquearlo y gestionar varios entornos.",
 "objetivos": [
  "Configurar un backend remoto en S3 con cifrado, versionado y bloqueo.",
  "Migrar un estado local a remoto.",
  "Comparar workspaces vs carpetas por entorno.",
  "Leer outputs de otra configuración con `terraform_remote_state`.",
 ],
 "temas": [
  "Backends: `local`, `s3`, `azurerm`, `gcs`, `remote`/`cloud` (HCP Terraform).",
  "Backend S3: bucket con versionado y cifrado; bloqueo nativo con `use_lockfile = true` (Terraform 1.10+). La tabla DynamoDB es el método antiguo, hoy obsoleto.",
  "El problema huevo-gallina: crear el bucket del estado (bootstrap).",
  "`terraform init -migrate-state` y `-reconfigure`. Configuración parcial con `-backend-config`.",
  "Bloqueos atascados: `terraform force-unlock`.",
  "Workspaces CLI (`terraform.workspace`) vs un directorio por entorno: ventajas e inconvenientes.",
  "HCP Terraform (antes Terraform Cloud): estado remoto, ejecuciones remotas, variables, plan gratuito.",
 ],
 "ejemplo": ("hcl", "backend.tf", """terraform {
  backend "s3" {
    bucket       = "mi-empresa-terraform-state"
    key          = "curso/dev/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true # bloqueo nativo en S3 (Terraform >= 1.10)
  }
}"""),
 "lab": {"titulo": "Estado remoto",
  "pasos": [
   "Crea (con Terraform, en una carpeta `bootstrap/`) un bucket con versionado y cifrado.",
   "Añade el bloque `backend \"s3\"` a tu proyecto y ejecuta `terraform init -migrate-state`.",
   "Abre dos terminales y lanza `apply` a la vez para ver el bloqueo.",
   "Crea los workspaces `dev` y `prod` y usa `terraform.workspace` en un nombre.",
  ]},
 "comandos": [
  ("terraform init -migrate-state", "Mueve el estado al nuevo backend."),
  ("terraform init -reconfigure", "Reinicializa el backend ignorando la configuración anterior."),
  ("terraform init -backend-config=dev.s3.tfbackend", "Configuración parcial del backend desde archivo."),
  ("terraform force-unlock LOCK_ID", "Libera un bloqueo atascado (¡asegúrate de que nadie está aplicando!)."),
  ("terraform workspace list", "Lista workspaces."),
  ("terraform workspace new dev", "Crea un workspace."),
  ("terraform workspace select prod", "Cambia de workspace."),
  ("terraform workspace show", "Muestra el workspace actual."),
  ("terraform login", "Inicia sesión en HCP Terraform."),
 ],
 "errores": [
  ("`Error acquiring the state lock`", "Alguien (o un proceso caído) tiene el bloqueo. Espera o usa `force-unlock` con cuidado."),
  ("Usar variables dentro del bloque `backend`", "No se permite. Usa `-backend-config` o archivos `.tfbackend`."),
 ],
 "quiz": [
  "¿Por qué el backend debe tener versionado activado?",
  "¿Cuándo preferirías carpetas por entorno en lugar de workspaces?",
 ],
},
{
 "num": "11", "slug": "modulos", "titulo": "Módulos",
 "nivel": "Intermedio", "duracion": "3 h",
 "resumen": "Empaquetar y reutilizar infraestructura: crear, versionar y consumir módulos.",
 "objetivos": [
  "Crear un módulo propio con entradas, salidas y documentación.",
  "Consumir módulos del Terraform Registry fijando versiones.",
  "Diseñar módulos con una responsabilidad clara.",
 ],
 "temas": [
  "Root module vs child modules. Estructura: `main.tf`, `variables.tf`, `outputs.tf`, `versions.tf`, `README.md`, `examples/`.",
  "Bloque `module`: `source`, `version`, entradas, `module.nombre.output`.",
  "Fuentes: ruta local, Registry público, Git (`?ref=v1.2.0`), registro privado.",
  "Meta-argumentos en módulos: `count`, `for_each`, `providers`, `depends_on`.",
  "Módulos populares: `terraform-aws-modules/vpc/aws`, `.../ec2-instance/aws`, `.../s3-bucket/aws`.",
  "Buenas prácticas: no envolver un único recurso, no configurar providers dentro del módulo, versionado semántico, documentar con `terraform-docs`.",
  "`terraform get` y `terraform init` para descargar módulos.",
 ],
 "ejemplo": ("hcl", "main.tf (raíz)", """module "web_bucket" {
  source = "./modules/static-site"

  nombre  = "mi-web"
  entorno = var.entorno
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = "curso-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-west-1a", "eu-west-1b"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24"]
}

output "bucket" {
  value = module.web_bucket.nombre_bucket
}"""),
 "lab": {"titulo": "Módulo de web estática",
  "pasos": [
   "Crea `modules/static-site` con un bucket S3 configurado como web.",
   "Expón el nombre del bucket y la URL como outputs.",
   "Instáncialo dos veces (dev y prod) con `for_each`.",
   "Sustituye tu VPC manual por el módulo oficial del Registry.",
   "Genera el README del módulo con `terraform-docs markdown table`.",
  ]},
 "comandos": [
  ("terraform get -update", "Descarga/actualiza los módulos."),
  ("terraform init -upgrade", "Actualiza módulos y providers."),
  ("terraform-docs markdown table ./modules/static-site", "Genera documentación de inputs/outputs."),
  ("terraform state list module.vpc", "Recursos dentro de un módulo."),
 ],
 "errores": [
  ("`Module not installed`", "Has añadido un módulo nuevo: ejecuta `terraform init`."),
  ("Módulos sin versión fija", "Fija siempre `version` (Registry) o `?ref=` (Git) para evitar sorpresas."),
 ],
 "quiz": [
  "¿Cómo accedes a un output de un módulo hijo?",
  "¿Por qué no se debe declarar el bloque `provider` dentro de un módulo reutilizable?",
 ],
},
{
 "num": "12", "slug": "import-refactor", "titulo": "Importar y refactorizar",
 "nivel": "Intermedio", "duracion": "1,5 h",
 "resumen": "Traer infraestructura existente a Terraform y reorganizar el código sin destruir nada.",
 "objetivos": [
  "Importar recursos creados a mano con el bloque `import`.",
  "Generar código automáticamente con `-generate-config-out`.",
  "Renombrar y mover recursos con `moved` y dejar de gestionarlos con `removed`.",
 ],
 "temas": [
  "Escenario real: infraestructura creada con la consola (ClickOps).",
  "Bloque `import` (Terraform 1.5+) vs el comando clásico `terraform import`.",
  "`terraform plan -generate-config-out=generado.tf` y cómo limpiar el código generado.",
  "Bloque `moved` para renombrar recursos o moverlos a módulos sin recrearlos.",
  "Bloque `removed` (1.7+) para soltar recursos del estado de forma declarativa.",
  "Herramientas externas: Terraformer, former2 (con espíritu crítico).",
 ],
 "ejemplo": ("hcl", "import.tf", """# 1. Importar un bucket creado a mano
import {
  to = aws_s3_bucket.legado
  id = "bucket-creado-a-mano"
}

# 2. Renombrar sin destruir
moved {
  from = aws_instance.servidor
  to   = aws_instance.web
}

# 3. Dejar de gestionar sin borrar
removed {
  from = aws_s3_bucket.antiguo

  lifecycle {
    destroy = false
  }
}"""),
 "lab": {"titulo": "Rescata un recurso hecho a mano",
  "pasos": [
   "Crea un bucket y un security group desde la consola web.",
   "Escribe los bloques `import` y ejecuta `terraform plan -generate-config-out=generado.tf`.",
   "Limpia el código generado y aplica hasta que el plan diga «No changes».",
   "Mueve el recurso a un módulo usando un bloque `moved`.",
  ]},
 "comandos": [
  ("terraform plan -generate-config-out=generado.tf", "Genera HCL para los bloques import sin código."),
  ("terraform import aws_s3_bucket.legado bucket-creado-a-mano", "Importación clásica por CLI."),
  ("terraform state mv aws_instance.a module.web.aws_instance.a", "Mover a un módulo (alternativa imperativa a `moved`)."),
 ],
 "errores": [
  ("El plan quiere modificar el recurso importado", "Tu código no coincide con la realidad. Ajusta argumentos hasta que no haya cambios."),
  ("ID de importación incorrecto", "Cada recurso usa un formato distinto: consulta la sección «Import» en la doc del provider."),
 ],
 "quiz": [
  "¿Qué ventaja tiene el bloque `import` frente al comando `terraform import`?",
  "¿Qué pasa si renombras un recurso sin un bloque `moved`?",
 ],
},
{
 "num": "13", "slug": "calidad-testing", "titulo": "Validación, testing y seguridad",
 "nivel": "Avanzado", "duracion": "2,5 h",
 "resumen": "Condiciones, tests nativos, linters y escáneres de seguridad.",
 "objetivos": [
  "Añadir `precondition`, `postcondition` y bloques `check`.",
  "Escribir tests con `terraform test` (archivos `.tftest.hcl`).",
  "Integrar TFLint, Trivy/Checkov y pre-commit.",
  "Gestionar secretos correctamente.",
 ],
 "temas": [
  "Niveles de validación: `validation` en variables → `precondition`/`postcondition` → `check` → tests.",
  "`terraform test`: bloques `run`, `command = plan|apply`, `assert`, `mock_provider` (1.7+).",
  "Análisis estático: `tflint` (errores y buenas prácticas del provider).",
  "Seguridad: `trivy config` (sucesor de tfsec) y `checkov`.",
  "Automatizar con `pre-commit` (fmt, validate, tflint, docs).",
  "Secretos: variables de entorno, AWS Secrets Manager/SSM, `ephemeral` y argumentos write-only en versiones recientes.",
  "Estimar costes con `infracost`.",
 ],
 "ejemplo": ("hcl", "tests/bucket.tftest.hcl", """variables {
  entorno = "dev"
}

run "nombre_correcto" {
  command = plan

  assert {
    condition     = startswith(aws_s3_bucket.web.bucket_prefix, "web-dev")
    error_message = "El prefijo del bucket debe empezar por web-dev"
  }
}

run "entorno_invalido" {
  command = plan

  variables {
    entorno = "pruebas"
  }

  expect_failures = [var.entorno]
}"""),
 "lab": {"titulo": "Red de seguridad",
  "pasos": [
   "Añade una `postcondition` que verifique que la instancia tiene IP pública.",
   "Escribe dos tests con `terraform test` (uno que pase, uno con `expect_failures`).",
   "Ejecuta `tflint --init && tflint` y corrige los avisos.",
   "Pasa `trivy config .` y arregla al menos un hallazgo.",
   "Configura `pre-commit` con los hooks de `antonbabenko/pre-commit-terraform`.",
  ]},
 "comandos": [
  ("terraform test", "Ejecuta los archivos *.tftest.hcl."),
  ("terraform test -filter=tests/bucket.tftest.hcl -verbose", "Ejecuta un test concreto con detalle."),
  ("tflint --init && tflint --recursive", "Descarga plugins y analiza el código."),
  ("trivy config .", "Escanea configuraciones inseguras."),
  ("checkov -d .", "Escáner de políticas de seguridad."),
  ("pre-commit run --all-files", "Lanza todos los hooks sobre el repositorio."),
  ("infracost breakdown --path .", "Estimación de costes mensuales."),
 ],
 "errores": [
  ("Tests con `command = apply` que crean recursos caros", "Usa `plan` o `mock_provider` siempre que sea posible."),
  ("Ignorar avisos de seguridad sin justificar", "Si suprimes una regla, deja un comentario explicando por qué."),
 ],
 "quiz": [
  "¿Diferencia entre una `postcondition` y un bloque `check`?",
  "¿Qué herramienta usarías para detectar un bucket público?",
 ],
},
{
 "num": "14", "slug": "equipo-cicd", "titulo": "Trabajo en equipo y CI/CD",
 "nivel": "Avanzado", "duracion": "2,5 h",
 "resumen": "Flujo con Git y Pull Requests, GitHub Actions con OIDC y HCP Terraform.",
 "objetivos": [
  "Organizar un repositorio de infraestructura para varios entornos.",
  "Automatizar `fmt`, `validate`, `plan` en cada Pull Request.",
  "Autenticar GitHub Actions en AWS sin claves (OIDC).",
  "Conocer HCP Terraform y alternativas (Atlantis, Spacelift, env0).",
 ],
 "temas": [
  "Estructura de repositorio: `modules/`, `envs/dev`, `envs/prod`, `bootstrap/`.",
  "Flujo GitOps: rama → PR → plan automático → revisión → merge → apply.",
  "Guardar el plan (`-out`) y aplicar exactamente ese plan.",
  "GitHub Actions: `hashicorp/setup-terraform`, caché de plugins, comentarios con el plan.",
  "OIDC: rol IAM de confianza para GitHub, sin secretos de larga duración.",
  "`TF_IN_AUTOMATION`, `-input=false`, `-no-color`, códigos de salida (`-detailed-exitcode`).",
  "Políticas como código: Sentinel / OPA (visión general).",
 ],
 "ejemplo": ("yaml", ".github/workflows/terraform.yml", """name: terraform
on:
  pull_request:
    paths: ["envs/**", "modules/**"]

permissions:
  id-token: write   # necesario para OIDC
  contents: read
  pull-requests: write

jobs:
  plan:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: envs/dev
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-terraform
          aws-region: eu-west-1
      - run: terraform fmt -check -recursive
      - run: terraform init -input=false
      - run: terraform validate
      - run: terraform plan -input=false -out=tfplan"""),
 "lab": {"titulo": "Pipeline de infraestructura",
  "pasos": [
   "Reorganiza tus labs en `modules/` + `envs/dev` + `envs/prod`.",
   "Crea el proveedor OIDC y el rol IAM para GitHub (¡con Terraform!).",
   "Añade el workflow de ejemplo y abre un PR para ver el plan.",
   "Añade un job de `apply` que solo se ejecute al hacer merge en `main`.",
  ]},
 "comandos": [
  ("terraform plan -out=tfplan", "Guarda el plan en un archivo."),
  ("terraform show tfplan", "Muestra el contenido de un plan guardado."),
  ("terraform apply tfplan", "Aplica exactamente el plan guardado."),
  ("terraform plan -detailed-exitcode", "Sale con 0 (sin cambios), 1 (error) o 2 (hay cambios)."),
  ("terraform -chdir=envs/dev plan", "Ejecuta en otra carpeta sin hacer `cd`."),
 ],
 "errores": [
  ("Guardar access keys de AWS como secretos de GitHub", "Usa OIDC con un rol de permisos mínimos."),
  ("Aplicar desde el portátil y desde CI a la vez", "Define una única vía de despliegue y respétala."),
 ],
 "quiz": [
  "¿Por qué conviene aplicar un plan guardado en lugar de lanzar `apply` de nuevo?",
  "¿Qué aporta OIDC frente a claves estáticas?",
 ],
},
{
 "num": "15", "slug": "proyecto-final", "titulo": "Proyecto final y certificación",
 "nivel": "Avanzado", "duracion": "4–6 h",
 "resumen": "Integrar todo en una infraestructura completa y preparar la certificación oficial.",
 "objetivos": [
  "Diseñar y desplegar una infraestructura de varios componentes con buenas prácticas.",
  "Documentar el proyecto como lo haría un equipo profesional.",
  "Conocer el temario de la certificación HashiCorp Certified: Terraform Associate.",
 ],
 "temas": [
  "Arquitectura propuesta: VPC con subredes públicas/privadas, Application Load Balancer, Auto Scaling Group con EC2, bucket S3 para estáticos, (opcional) RDS.",
  "Requisitos: módulos propios + Registry, backend remoto, dos entornos, variables validadas, tests, CI con plan en PR.",
  "Entregables: código, README con diagrama, outputs útiles, evidencia de `destroy`.",
  "Rúbrica de evaluación: funcionalidad, organización, seguridad, documentación, coste.",
  "Certificación Terraform Associate: dominios del examen, formato, simulacros y recursos oficiales (consulta la versión vigente del examen en la web de HashiCorp).",
  "Siguientes pasos: Kubernetes con Terraform, Terragrunt, OpenTofu, otras nubes, CDK for Terraform.",
 ],
 "ejemplo": ("text", "Estructura sugerida", """proyecto-final/
├── bootstrap/            # bucket del estado remoto
├── modules/
│   ├── network/          # VPC, subredes, NAT
│   ├── web/              # ALB + ASG + security groups
│   └── static-site/      # S3 (+ CloudFront opcional)
├── envs/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   └── dev.tfvars
│   └── prod/
├── tests/
├── .github/workflows/terraform.yml
├── .pre-commit-config.yaml
├── .tflint.hcl
└── README.md"""),
 "lab": {"titulo": "Web escalable en AWS",
  "pasos": [
   "Dibuja el diagrama de arquitectura antes de escribir código.",
   "Implementa los módulos `network`, `web` y `static-site`.",
   "Despliega `dev` desde CI y comprueba la URL del balanceador.",
   "Ejecuta `infracost` y documenta el coste estimado.",
   "Destruye todo y deja constancia en el README.",
  ]},
 "comandos": [
  ("terraform plan -var-file=prod.tfvars -out=prod.tfplan", "Plan de producción guardado."),
  ("terraform destroy -var-file=dev.tfvars", "Limpieza final del entorno."),
 ],
 "errores": [
  ("Olvidar destruir el NAT Gateway o el ALB", "Son de los recursos que más cobran por hora. Revisa la factura al día siguiente."),
 ],
 "quiz": [
  "Explica tu decisión entre workspaces y carpetas por entorno.",
  "¿Qué mejorarías para llevar este proyecto a producción real?",
 ],
},
]
