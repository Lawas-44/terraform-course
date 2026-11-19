# -*- coding: utf-8 -*-
# Módulo 15 · Proyecto final y certificación

LECCION = [
 ("h", "El proyecto"),
 ("p", "Vas a montar una **web que aguanta muchas visitas**, usando todo lo aprendido. Tiene estas piezas:"),
 ("ul", [
  "**Red (VPC)**: el espacio privado donde viven tus recursos, con subredes en dos zonas.",
  "**Balanceador de carga (ALB)**: recibe las visitas y las reparte entre los servidores.",
  "**Grupo de servidores (Auto Scaling)**: entre 2 y 4 servidores iguales. Si uno falla, se crea otro.",
 ]),
 ("code", "text", "esquema", """            Internet
               |
     +---------v---------+
     |    Balanceador    |
     +---------+---------+
               |
       +-------+-------+
       |               |
  +----v----+     +----v----+
  | servidor|     | servidor|
  +---------+     +---------+"""),
 ("warn", "El balanceador **no es gratis** (unos 20 dólares al mes si lo dejas encendido). Crea, prueba y borra en la misma sesión."),

 ("h", "Requisitos"),
 ("table", ["#", "Qué debe tener", "Módulo"], [
  ["1", "Estado guardado en S3 con bloqueo", "10"],
  ["2", "Módulos propios: `network` y `web`", "11"],
  ["3", "Dos entornos: `envs/dev` y `envs/prod`", "14"],
  ["4", "Variables con tipo, descripción y validación", "4"],
  ["5", "Subredes creadas con `for_each`", "7"],
  ["6", "Output con la dirección web", "4"],
  ["7", "Al menos un test con `terraform test`", "13"],
  ["8", "GitHub Actions con `plan` en cada Pull Request", "14"],
  ["9", "Sin contraseñas en el código", "13"],
  ["10", "README explicando cómo usarlo", "15"],
 ]),

 ("h", "El módulo de red"),
 ("p", "Crea la red y una subred pública en cada zona. Fíjate cómo `for_each` y `cidrsubnet` calculan las subredes solas:"),
 ("code", "hcl", "modules/network/main.tf", """data "aws_availability_zones" "disponibles" {
  state = "available"
}

locals {
  zonas = slice(data.aws_availability_zones.disponibles.names, 0, var.num_zonas)
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  tags                 = { Name = var.nombre }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id
}

resource "aws_subnet" "publica" {
  for_each = { for i, az in local.zonas : az => i }

  vpc_id                  = aws_vpc.this.id
  availability_zone       = each.key
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, each.value)
  map_public_ip_on_launch = true
}

resource "aws_route_table" "publica" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }
}

resource "aws_route_table_association" "publica" {
  for_each       = aws_subnet.publica
  subnet_id      = each.value.id
  route_table_id = aws_route_table.publica.id
}"""),
 ("p", "El código completo de los dos módulos (con sus variables y outputs) está en la carpeta `labs/15-proyecto-final` del repositorio."),

 ("h", "El módulo web"),
 ("p", "Este módulo crea el balanceador, los servidores y dos firewalls: uno para el balanceador (abierto a Internet) y otro para los servidores (solo acepta visitas que vengan del balanceador). Las partes principales:"),
 ("code", "hcl", "modules/web/main.tf (resumen)", """# Balanceador
resource "aws_lb" "this" {
  name_prefix        = "web-"
  load_balancer_type = "application"
  subnets            = var.subnet_ids
  security_groups    = [aws_security_group.alb.id]
}

# Plantilla para crear servidores iguales
resource "aws_launch_template" "this" {
  name_prefix   = "${var.nombre}-"
  image_id      = data.aws_ami.al2023.id
  instance_type = var.tipo_instancia
  # ... script que instala nginx ...
}

# Grupo de servidores
resource "aws_autoscaling_group" "this" {
  min_size            = var.min_instancias
  max_size            = var.max_instancias
  vpc_zone_identifier = var.subnet_ids
  target_group_arns   = [aws_lb_target_group.this.arn]

  launch_template {
    id      = aws_launch_template.this.id
    version = "$Latest"
  }
}

output "url" {
  value = "http://${aws_lb.this.dns_name}"
}"""),

 ("h", "El entorno dev"),
 ("code", "hcl", "envs/dev/main.tf", """module "network" {
  source   = "../../modules/network"
  nombre   = "pf-dev"
  vpc_cidr = "10.0.0.0/16"
}

module "web" {
  source         = "../../modules/web"
  nombre         = "pf-dev"
  vpc_id         = module.network.vpc_id
  subnet_ids     = module.network.public_subnet_ids
  tipo_instancia = "t3.micro"
  min_instancias = 2
  max_instancias = 2
}

output "url" {
  value = module.web.url
}"""),
 ("term", """$ cd envs/dev
$ terraform init
$ terraform apply
...
Outputs:
url = "http://web-20261119-1234567890.eu-west-1.elb.amazonaws.com"

$ curl http://web-20261119-1234567890.eu-west-1.elb.amazonaws.com
<h1>pf-dev</h1><p>Servido por i-0aaa111</p>
$ curl http://web-20261119-1234567890.eu-west-1.elb.amazonaws.com
<h1>pf-dev</h1><p>Servido por i-0bbb222</p>"""),
 ("p", "Cada visita la atiende un servidor distinto: el balanceador está repartiendo el trabajo."),
 ("tip", "Los servidores tardan 2 o 3 minutos en estar listos. Hasta entonces verás errores 502 o 503."),

 ("h", "Cómo se evalúa"),
 ("table", ["Criterio", "Peso", "Qué se valora"], [
  ["Funciona", "30 %", "Se crea y se borra sin errores, y la web responde"],
  ["Organización", "20 %", "Módulos claros y entornos separados"],
  ["Seguridad", "20 %", "Sin contraseñas en el código; servidores solo accesibles desde el balanceador"],
  ["Automatización", "15 %", "GitHub Actions con fmt, validate y plan; tests que pasan"],
  ["Documentación", "15 %", "README con esquema e instrucciones"],
 ]),

 ("h", "La certificación oficial"),
 ("p", "HashiCorp ofrece la certificación **Terraform Associate**, que valida lo que has aprendido en este curso. Es un examen online de unos 60 minutos con preguntas tipo test. Consulta los detalles actualizados en la web de HashiCorp."),
 ("p", "Para prepararla:"),
 ("ol", [
  "Repasa la chuleta de comandos hasta saber qué hace cada uno.",
  "Repite los tests de todos los módulos hasta aprobarlos.",
  "Haz el simulacro de este módulo.",
  "Practica escribiendo código: es la mejor preparación.",
 ]),
]

TEST = [
 ("Simulacro · ¿Qué comando debes ejecutar tras añadir un nuevo provider al código?",
  ["terraform plan", "terraform init", "terraform refresh", "terraform providers"], 1,
  "Cualquier provider o módulo nuevo requiere init."),
 ("Simulacro · ¿Qué afirmación sobre el estado es FALSA?",
  ["Puede contener secretos", "Debe guardarse en un backend remoto en equipos", "Terraform lo necesita para funcionar", "Es seguro subirlo a un repositorio público si se marca sensitive"], 3,
  "`sensitive` no cifra nada en el estado."),
 ("Simulacro · ¿Qué hace `terraform apply -refresh-only`?",
  ["Recrea todos los recursos", "Actualiza el estado para que refleje la realidad sin modificar la infraestructura", "Destruye el drift", "Actualiza los providers"], 1,
  "Sincroniza estado ← realidad, previa confirmación."),
 ("Simulacro · Tienes `variable \"x\" { default = 1 }`, `TF_VAR_x=2` y `x = 3` en terraform.tfvars. ¿Valor de var.x?",
  ["1", "2", "3", "Error"], 2, "terraform.tfvars tiene prioridad sobre las variables de entorno."),
 ("Simulacro · ¿Qué meta-argumento evita recrear recursos al quitar un elemento intermedio de una colección?",
  ["count", "for_each", "depends_on", "provider"], 1, "for_each identifica cada copia por clave, no por posición."),
 ("Simulacro · ¿Dónde se guardan los providers descargados por init?",
  ["En ~/.aws", "En la carpeta .terraform del proyecto", "En el estado", "En el lock file"], 1,
  "El lock file solo guarda versiones y hashes; los binarios van a .terraform/."),
 ("Simulacro · ¿Qué variable de entorno activa los logs detallados de Terraform?",
  ["TF_DEBUG", "TF_LOG", "TERRAFORM_VERBOSE", "TF_VAR_log"], 1, "TF_LOG=TRACE|DEBUG|INFO|WARN|ERROR; TF_LOG_PATH para guardarlos."),
 ("Simulacro · ¿Cómo referencias el output `vpc_id` del módulo `network`?",
  ["network.vpc_id", "module.network.vpc_id", "output.network.vpc_id", "data.network.vpc_id"], 1, "module.NOMBRE.OUTPUT."),
 ("Simulacro · ¿Qué bloque permite renombrar un recurso sin destruirlo y queda registrado en el código?",
  ["import", "moved", "removed", "rename"], 1, "Disponible desde Terraform 1.1."),
 ("Simulacro · ¿Qué es cierto sobre los workspaces CLI?",
  ["Cada uno tiene su propio estado con el mismo código", "Cada uno tiene su propio código", "Sustituyen al backend", "Solo existen en HCP Terraform"], 0,
  "Mismo código, estados separados; `terraform.workspace` da el nombre actual."),
]

RETOS = [
 {"titulo": "Entorno prod",
  "enunciado": "Crea `envs/prod` reutilizando los módulos, con otra `key` de estado, otra VPC (`10.10.0.0/16`), 3 zonas y entre 2 y 4 instancias `t3.small`.",
  "pista": "Copia `envs/dev` y cambia solo lo necesario. Comprueba con `terraform plan` que no toca nada de dev.",
  "solucion": ("hcl", """# envs/prod/main.tf (lo que cambia respecto a dev)
#   backend:  key = "proyecto-final/prod/terraform.tfstate"
#   tags:     Entorno = "prod"

module "network" {
  source    = "../../modules/network"
  nombre    = "pf-prod"
  vpc_cidr  = "10.10.0.0/16"
  num_zonas = 3
}

module "web" {
  source         = "../../modules/web"
  nombre         = "pf-prod"
  vpc_id         = module.network.vpc_id
  subnet_ids     = module.network.public_subnet_ids
  tipo_instancia = "t3.small"
  min_instancias = 2
  max_instancias = 4
}""")},
 {"titulo": "Test del módulo network con mocks",
  "enunciado": "Escribe `modules/network/tests/network.tftest.hcl` con un `mock_provider \"aws\"` que compruebe que con `num_zonas = 3` se crean 3 subredes y que la primera tiene el CIDR `10.0.0.0/24`.",
  "pista": "El data source de zonas también se mockea: `mock_data \"aws_availability_zones\" { defaults = { names = [...] } }`.",
  "solucion": ("hcl", """mock_provider "aws" {
  mock_data "aws_availability_zones" {
    defaults = {
      names = ["eu-west-1a", "eu-west-1b", "eu-west-1c"]
    }
  }
}

variables {
  nombre    = "test"
  num_zonas = 3
}

run "tres_subredes" {
  command = apply

  assert {
    condition     = length(aws_subnet.publica) == 3
    error_message = "Deberían crearse 3 subredes"
  }

  assert {
    condition     = aws_subnet.publica["eu-west-1a"].cidr_block == "10.0.0.0/24"
    error_message = "CIDR inesperado en la primera subred"
  }
}""")},
]
