# -*- coding: utf-8 -*-
# Módulo 15 · Proyecto final y certificación

LECCION = [
 ("h", "El proyecto"),
 ("p", "Vas a construir, de principio a fin, la infraestructura de una **web escalable** en AWS aplicando todo lo aprendido. Es un proyecto ideal para tu portfolio y para preparar la certificación."),
 ("code", "text", "arquitectura", """                         Internet
                            │
                  ┌─────────▼──────────┐
                  │ Application Load   │   subredes públicas
                  │ Balancer (ALB)     │   (2 zonas)
                  └─────────┬──────────┘
                            │ :80
          ┌─────────────────┼─────────────────┐
          │      Auto Scaling Group (2-4)     │   subredes
          │   ┌──────────┐     ┌──────────┐   │   (2 zonas)
          │   │ EC2 nginx│     │ EC2 nginx│   │
          │   └──────────┘     └──────────┘   │
          └───────────────────────────────────┘

          S3 (estáticos)          S3 (estado remoto) + lock"""),
 ("warn", "El Application Load Balancer **no es gratuito** (unos 0,025 USD/hora + tráfico, ≈ 20 USD/mes). Despliega, prueba y **destruye en la misma sesión**. Evita el NAT Gateway: en este diseño las instancias van en subredes públicas protegidas por security groups para ahorrar costes."),

 ("h", "Requisitos"),
 ("table", ["#", "Requisito", "Módulos del curso"], [
  ["1", "Estado remoto en S3 con `use_lockfile` (bootstrap separado)", "10"],
  ["2", "Módulos propios: `network`, `web`; y al menos uno del Registry", "11"],
  ["3", "Dos entornos (`envs/dev`, `envs/prod`) con distinto tamaño/réplicas", "4, 14"],
  ["4", "Variables con tipos, descripciones y validaciones", "4, 13"],
  ["5", "`for_each` o `count` para subredes", "7, 8"],
  ["6", "Outputs: URL del balanceador, IDs de red", "4"],
  ["7", "Al menos un `terraform test` (puede usar mocks)", "13"],
  ["8", "CI: fmt, validate, tflint y plan en cada PR", "14"],
  ["9", "Sin secretos en el código; Trivy sin hallazgos HIGH sin justificar", "13"],
  ["10", "README con diagrama, instrucciones y coste estimado", "13, 15"],
 ]),

 ("h", "Módulo network"),
 ("p", "Te damos el esqueleto de los módulos para que no partas de cero. Complétalos y mejóralos."),
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
  tags   = { Name = var.nombre }
}

resource "aws_subnet" "publica" {
  for_each = { for i, az in local.zonas : az => i }

  vpc_id                  = aws_vpc.this.id
  availability_zone       = each.key
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, each.value)
  map_public_ip_on_launch = true
  tags                    = { Name = "${var.nombre}-publica-${each.key}" }
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
 ("code", "hcl", "modules/network/variables.tf + outputs.tf", """variable "nombre" {
  type = string
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr debe ser un CIDR válido."
  }
}

variable "num_zonas" {
  type    = number
  default = 2
  validation {
    condition     = var.num_zonas >= 2 && var.num_zonas <= 3
    error_message = "Entre 2 y 3 zonas (el ALB necesita al menos 2)."
  }
}

output "vpc_id" {
  value = aws_vpc.this.id
}

output "public_subnet_ids" {
  value = [for s in aws_subnet.publica : s.id]
}"""),

 ("h", "Módulo web"),
 ("code", "hcl", "modules/web/main.tf", """data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# --- Security groups ---
resource "aws_security_group" "alb" {
  name_prefix = "${var.nombre}-alb-"
  vpc_id      = var.vpc_id
}

resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  # trivy:ignore:AVD-AWS-0107 El balanceador es público por diseño
  security_group_id = aws_security_group.alb.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "alb_a_app" {
  security_group_id            = aws_security_group.alb.id
  referenced_security_group_id = aws_security_group.app.id
  from_port                    = 80
  to_port                      = 80
  ip_protocol                  = "tcp"
}

resource "aws_security_group" "app" {
  name_prefix = "${var.nombre}-app-"
  vpc_id      = var.vpc_id
}

# Las instancias SOLO aceptan tráfico del balanceador
resource "aws_vpc_security_group_ingress_rule" "app_desde_alb" {
  security_group_id            = aws_security_group.app.id
  referenced_security_group_id = aws_security_group.alb.id
  from_port                    = 80
  to_port                      = 80
  ip_protocol                  = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "app_salida" {
  security_group_id = aws_security_group.app.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# --- Balanceador ---
resource "aws_lb" "this" {
  name_prefix        = "web-"
  load_balancer_type = "application"
  subnets            = var.subnet_ids
  security_groups    = [aws_security_group.alb.id]
}

resource "aws_lb_target_group" "this" {
  name_prefix = "web-"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = var.vpc_id

  health_check {
    path    = "/"
    matcher = "200"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.this.arn
  }
}

# --- Servidores ---
resource "aws_launch_template" "this" {
  name_prefix            = "${var.nombre}-"
  image_id               = data.aws_ami.al2023.id
  instance_type          = var.tipo_instancia
  vpc_security_group_ids = [aws_security_group.app.id]

  metadata_options {
    http_tokens = "required"
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    dnf install -y nginx
    TOKEN=$(curl -s -X PUT http://169.254.169.254/latest/api/token \\
      -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
    ID=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \\
      http://169.254.169.254/latest/meta-data/instance-id)
    echo "<h1>${var.nombre}</h1><p>Servido por $ID</p>" > /usr/share/nginx/html/index.html
    systemctl enable --now nginx
  EOF
  )
}

resource "aws_autoscaling_group" "this" {
  name_prefix         = "${var.nombre}-"
  min_size            = var.min_instancias
  max_size            = var.max_instancias
  desired_capacity    = var.min_instancias
  vpc_zone_identifier = var.subnet_ids
  target_group_arns   = [aws_lb_target_group.this.arn]
  health_check_type   = "ELB"

  launch_template {
    id      = aws_launch_template.this.id
    version = "$Latest"
  }

  instance_refresh {
    strategy = "Rolling"
  }

  tag {
    key                 = "Name"
    value               = var.nombre
    propagate_at_launch = true
  }
}"""),
 ("code", "hcl", "modules/web/variables.tf + outputs.tf", """variable "nombre" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }

variable "tipo_instancia" {
  type    = string
  default = "t3.micro"
}

variable "min_instancias" {
  type    = number
  default = 2
}

variable "max_instancias" {
  type    = number
  default = 4
  validation {
    condition     = var.max_instancias <= 6
    error_message = "Máximo 6 instancias para controlar el coste."
  }
}

output "url" {
  value = "http://${aws_lb.this.dns_name}"
}"""),

 ("h", "El entorno dev"),
 ("code", "hcl", "envs/dev/main.tf", """terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
  backend "s3" {
    bucket       = "tfstate-123456789012-eu-west-1"
    key          = "proyecto-final/dev/terraform.tfstate"
    region       = "eu-west-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = "eu-west-1"
  default_tags {
    tags = { Proyecto = "proyecto-final", Entorno = "dev", Gestion = "terraform" }
  }
}

module "network" {
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
 ("term", """$ cd envs/dev && terraform init && terraform apply
...
Plan: 19 to add, 0 to change, 0 to destroy.
...
Outputs:
url = "http://web-20261119123456-1234567890.eu-west-1.elb.amazonaws.com"

$ for i in 1 2 3 4; do curl -s $(terraform output -raw url); echo; done
<h1>pf-dev</h1><p>Servido por i-0aaa111</p>
<h1>pf-dev</h1><p>Servido por i-0bbb222</p>
<h1>pf-dev</h1><p>Servido por i-0aaa111</p>
<h1>pf-dev</h1><p>Servido por i-0bbb222</p>"""),
 ("p", "¡El balanceador reparte las peticiones entre las dos instancias! Las instancias tardan 2-3 minutos en pasar el *health check*; hasta entonces verás errores 502/503."),

 ("h", "Ideas para subir de nivel"),
 ("ul", [
  "Mover las instancias a **subredes privadas** con NAT Gateway (o VPC endpoints) — es lo correcto en producción, aunque cueste más.",
  "Añadir **HTTPS** con un certificado de ACM y un dominio en Route 53.",
  "Una política de **autoescalado** por CPU (`aws_autoscaling_policy` con *target tracking*).",
  "Una base de datos **RDS** en subredes privadas con `manage_master_user_password`.",
  "**CloudFront** delante del bucket de estáticos.",
  "Alarmas de **CloudWatch** y un dashboard, todo en Terraform.",
 ]),

 ("h", "Rúbrica de evaluación"),
 ("table", ["Criterio", "Peso", "Excelente si…"], [
  ["Funciona", "30 %", "Despliega y destruye a la primera; la URL responde desde varias instancias"],
  ["Organización", "20 %", "Módulos con responsabilidad clara, entornos separados, nombres consistentes"],
  ["Seguridad", "20 %", "Sin secretos, IMDSv2, instancias solo accesibles desde el ALB, escáner limpio"],
  ["Automatización", "15 %", "CI con fmt/validate/tflint/plan; tests que pasan"],
  ["Documentación", "15 %", "README con diagrama, cómo desplegar, outputs y coste estimado"],
 ]),

 ("h", "La certificación Terraform Associate"),
 ("p", "La certificación **HashiCorp Certified: Terraform Associate** valida los conocimientos de este curso. Datos orientativos (compruébalos siempre en la web oficial de HashiCorp, porque cambian con cada versión del examen):"),
 ("ul", [
  "Formato: online y supervisado, unos 60 minutos, preguntas de opción múltiple, verdadero/falso y respuesta corta.",
  "Validez: 2 años.",
  "Nivel: el de este curso. No hace falta experiencia profesional previa.",
 ]),
 ("p", "Temas que más se preguntan y dónde los has visto:"),
 ("table", ["Tema", "Módulo"], [
  ["Ventajas de IaC y de Terraform frente a otras herramientas", "00"],
  ["Flujo init / validate / plan / apply / destroy y qué hace cada uno", "02"],
  ["Restricciones de versión, lock file, `init -upgrade`", "05"],
  ["Precedencia de variables, tipos, `sensitive`", "04"],
  ["count vs for_each, dynamic, funciones (`lookup`, `merge`, `toset`, `cidrsubnet`)", "07, 08"],
  ["Estado: para qué sirve, comandos `state`, drift, `-refresh-only`, `-replace`", "09"],
  ["Backends, bloqueo, configuración parcial, workspaces", "10"],
  ["Módulos: fuentes, versiones, inputs/outputs, Registry", "11"],
  ["`import`, `moved`, logs con `TF_LOG`", "12"],
  ["HCP Terraform: workspaces remotos, ejecuciones, Sentinel, registro privado", "10, 14"],
 ]),
 ("p", "Consejos para el examen:"),
 ("ol", [
  "Repasa la **chuleta de comandos** del curso hasta saber qué hace cada flag.",
  "Haz los **tests de autoevaluación** de todos los módulos y repite los que no aprobaste.",
  "Lee los tutoriales oficiales de *developer.hashicorp.com/terraform* y su guía de estudio.",
  "Practica, practica: escribir código es la mejor preparación. Las preguntas son muy prácticas.",
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
