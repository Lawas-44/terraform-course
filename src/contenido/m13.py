# -*- coding: utf-8 -*-
# Módulo 13 · Validación, testing y seguridad

LECCION = [
 ("h", "Capas de protección"),
 ("p", "Cuanto antes detectes un error, más barato es arreglarlo. Terraform y su ecosistema ofrecen varias capas, de la más temprana a la más tardía:"),
 ("table", ["Capa", "Cuándo actúa", "Detecta"], [
  ["`terraform fmt` / `validate`", "Al escribir", "Sintaxis, tipos, referencias rotas"],
  ["Linters (TFLint)", "Al escribir / en CI", "Tipos de instancia inexistentes, malas prácticas"],
  ["Escáneres (Trivy, Checkov)", "En CI", "Configuraciones inseguras"],
  ["`validation` en variables", "En el plan", "Valores de entrada incorrectos"],
  ["`precondition` / `postcondition`", "En plan y apply", "Suposiciones sobre recursos"],
  ["Bloques `check`", "Al final del plan/apply", "Salud de la infraestructura (avisos)"],
  ["`terraform test`", "En CI", "Que el módulo hace lo que debe"],
 ]),

 ("h", "Preconditions y postconditions"),
 ("p", "Ya conoces `validation` en variables. Las **condiciones** van más allá: se ponen dentro del `lifecycle` de un recurso (o en un output) y pueden usar cualquier valor, incluidos atributos de otros recursos."),
 ("code", "hcl", "condiciones", """data "aws_ami" "elegida" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = [var.patron_ami]
  }
}

resource "aws_instance" "web" {
  ami           = data.aws_ami.elegida.id
  instance_type = var.tipo_instancia

  lifecycle {
    # ANTES de crear: comprueba las suposiciones
    precondition {
      condition     = data.aws_ami.elegida.architecture == "x86_64"
      error_message = "La AMI debe ser x86_64; ${data.aws_ami.elegida.name} no lo es."
    }

    # DESPUÉS de crear: comprueba el resultado
    postcondition {
      condition     = self.public_ip != ""
      error_message = "La instancia debería tener IP pública."
    }
  }
}

output "url" {
  value = "http://${aws_instance.web.public_dns}"

  precondition {
    condition     = aws_instance.web.public_dns != ""
    error_message = "Sin DNS público no hay URL."
  }
}"""),
 ("ul", [
  "`precondition` se evalúa antes de crear/modificar el recurso. Si falla, el plan se detiene.",
  "`postcondition` se evalúa después y puede usar `self` (el propio recurso).",
  "Si una condición falla, Terraform **para con un error**.",
 ]),

 ("h", "Bloques check: avisos, no errores"),
 ("p", "Un bloque `check` (Terraform 1.5+) verifica algo sobre la infraestructura **sin bloquear** el despliegue: si falla, muestra un aviso. Ideal para comprobaciones de salud. Puede incluir su propio data source:"),
 ("code", "hcl", "check.tf", """check "web_responde" {
  data "http" "home" {
    url = "http://${aws_instance.web.public_ip}"
  }

  assert {
    condition     = data.http.home.status_code == 200
    error_message = "La web devolvió ${data.http.home.status_code} en lugar de 200."
  }
}"""),
 ("term", """╷
│ Warning: Check block assertion failed
│
│   on check.tf line 7, in check "web_responde":
│    7:     condition     = data.http.home.status_code == 200
│
│ La web devolvió 502 en lugar de 200.
╵"""),
 ("info", "El data source `http` pertenece al provider `hashicorp/http`; añádelo a `required_providers`."),

 ("h", "terraform test"),
 ("p", "Desde la versión 1.6, Terraform tiene un framework de pruebas integrado. Los tests se escriben en HCL en archivos `*.tftest.hcl` (normalmente en la carpeta `tests/`). Vamos a probar un pequeño módulo sin nube:"),
 ("code", "hcl", "main.tf (módulo a probar)", """variable "proyecto" {
  type = string
  validation {
    condition     = length(var.proyecto) >= 3
    error_message = "proyecto debe tener al menos 3 caracteres."
  }
}

variable "entorno" {
  type    = string
  default = "dev"
}

locals {
  prefijo = "${var.proyecto}-${var.entorno}"
}

resource "local_file" "config" {
  filename = "${path.module}/${local.prefijo}.conf"
  content  = "proyecto=${var.proyecto}\\nentorno=${var.entorno}\\n"
}

output "prefijo" {
  value = local.prefijo
}"""),
 ("code", "hcl", "tests/config.tftest.hcl", """# Variables comunes a todos los run
variables {
  proyecto = "tienda"
}

run "prefijo_por_defecto" {
  command = plan   # no crea nada: rápido y gratis

  assert {
    condition     = output.prefijo == "tienda-dev"
    error_message = "El prefijo por defecto debería ser tienda-dev"
  }
}

run "archivo_en_prod" {
  command = apply  # crea de verdad (y lo destruye al terminar)

  variables {
    entorno = "prod"
  }

  assert {
    condition     = local_file.config.filename == "./tienda-prod.conf"
    error_message = "Nombre de archivo incorrecto: ${local_file.config.filename}"
  }

  assert {
    condition     = strcontains(local_file.config.content, "entorno=prod")
    error_message = "El contenido no incluye el entorno"
  }
}

run "rechaza_nombres_cortos" {
  command = plan

  variables {
    proyecto = "ab"
  }

  # Esperamos que la validación falle: el test PASA si falla
  expect_failures = [var.proyecto]
}"""),
 ("term", """$ terraform init
$ terraform test
tests/config.tftest.hcl... in progress
  run "prefijo_por_defecto"... pass
  run "archivo_en_prod"... pass
  run "rechaza_nombres_cortos"... pass
tests/config.tftest.hcl... tearing down
tests/config.tftest.hcl... pass

Success! 3 passed, 0 failed."""),
 ("ul", [
  "Cada `run` ejecuta un `plan` o un `apply` y comprueba sus `assert`.",
  "Los `run` se ejecutan en orden y comparten estado; al final, Terraform **destruye** todo lo creado.",
  "`expect_failures` sirve para probar que las validaciones rechazan valores incorrectos.",
 ]),

 ("h", "Mocks: probar módulos de AWS gratis"),
 ("p", "Con `command = apply` contra AWS los tests crean recursos reales (lentos y con coste). Desde Terraform 1.7 puedes **simular** un provider con `mock_provider`: los recursos «se crean» con valores inventados, sin llamar a la API ni necesitar credenciales."),
 ("code", "hcl", "tests/bucket.tftest.hcl", """mock_provider "aws" {
  # valores falsos para atributos calculados
  mock_resource "aws_s3_bucket" {
    defaults = {
      arn = "arn:aws:s3:::bucket-de-prueba"
    }
  }
}

variables {
  nombre  = "curso"
  entorno = "dev"
}

run "crea_bucket_con_prefijo" {
  command = apply   # aplicado contra el mock: gratis e instantáneo

  assert {
    condition     = startswith(aws_s3_bucket.this.bucket_prefix, "curso-dev-")
    error_message = "Prefijo de bucket incorrecto"
  }

  assert {
    condition     = aws_s3_object.index.content_type == "text/html"
    error_message = "index.html debe servirse como text/html"
  }
}"""),

 ("h", "Linters: TFLint"),
 ("p", "`terraform validate` no sabe si `t3.micra` es un tipo de instancia válido: para él es solo un string. **TFLint** con el plugin de AWS sí lo sabe, y además avisa de malas prácticas (variables sin tipo, declaraciones sin usar…)."),
 ("code", "hcl", ".tflint.hcl", """plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

plugin "aws" {
  enabled = true
  version = "0.38.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}"""),
 ("term", """$ tflint --init
Installing "aws" plugin...
$ tflint
2 issue(s) found:

Error: "t3.micra" is an invalid value as instance_type (aws_instance_invalid_type)
  on main.tf line 12:
  12:   instance_type = "t3.micra"

Warning: variable "region" is declared but not used (terraform_unused_declarations)
  on variables.tf line 1:"""),
 ("info", "La versión del plugin `aws` cambia a menudo; consulta la última en su repositorio de GitHub."),

 ("h", "Escáneres de seguridad: Trivy y Checkov"),
 ("p", "Estas herramientas revisan tu código contra cientos de reglas de seguridad: buckets públicos, discos sin cifrar, puertos abiertos a todo Internet, logs desactivados…"),
 ("code", "bash", "terminal", """# Trivy (de Aqua Security; incluye las reglas del antiguo tfsec)
trivy config .

# Checkov (de Palo Alto / Bridgecrew)
pip install checkov
checkov -d ."""),
 ("term", """$ trivy config .
main.tf (terraform)
Tests: 12 (SUCCESSES: 9, FAILURES: 3)
Failures: 3 (HIGH: 2, MEDIUM: 1)

HIGH: Security group rule allows ingress from public internet.
════════════════════════════════════════
  main.tf:15
  15 │   cidr_ipv4 = "0.0.0.0/0"
...
HIGH: Instance does not require IMDS access to require a token
  main.tf:20-35"""),
 ("p", "No todos los avisos son problemas reales (una web pública *debe* aceptar tráfico de Internet). Cuando aceptes un riesgo, documenta la excepción en el código:"),
 ("code", "hcl", "ignorar con justificación", """resource "aws_vpc_security_group_ingress_rule" "http" {
  # trivy:ignore:AVD-AWS-0107 Web pública: debe aceptar HTTP desde Internet
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}"""),
 ("p", "Y arregla lo que sí es un problema. Por ejemplo, exigir IMDSv2 en las instancias:"),
 ("code", "hcl", "IMDSv2", """resource "aws_instance" "web" {
  # ...
  metadata_options {
    http_tokens = "required"
  }
}"""),

 ("h", "Automatizar todo con pre-commit"),
 ("p", "**pre-commit** ejecuta comprobaciones automáticamente cada vez que haces `git commit`. El proyecto `pre-commit-terraform` trae hooks listos:"),
 ("code", "yaml", ".pre-commit-config.yaml", """repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.96.1   # usa la última versión publicada
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint
      - id: terraform_trivy
      - id: terraform_docs"""),
 ("code", "bash", "terminal", """pip install pre-commit
pre-commit install            # activa el hook en este repo
pre-commit run --all-files    # ejecútalo ahora sobre todo"""),

 ("h", "Secretos: cómo gestionarlos"),
 ("p", "Recapitulando lo que sabemos sobre secretos (contraseñas, tokens, claves):"),
 ("ol", [
  "Nunca en archivos `.tf` ni en `.tfvars` subidos a Git.",
  "Pásalos como variables `sensitive` desde variables de entorno (`TF_VAR_db_password`) o desde el gestor de secretos del CI.",
  "Mejor aún: que no pasen por Terraform. Deja que AWS los genere y los guarde:",
 ]),
 ("code", "hcl", "contraseña gestionada por AWS", """resource "aws_db_instance" "app" {
  identifier          = "app-db"
  engine              = "postgres"
  instance_class      = "db.t4g.micro"
  allocated_storage   = 20
  username            = "app"
  skip_final_snapshot = true

  # AWS genera la contraseña y la guarda en Secrets Manager.
  # Terraform nunca la conoce, así que NO acaba en el estado.
  manage_master_user_password = true
}"""),
 ("ul", [
  "Lee secretos existentes con data sources (`aws_secretsmanager_secret_version`, `aws_ssm_parameter`), sabiendo que su valor sí acabará en el estado.",
  "Las versiones recientes de Terraform (1.10+) añaden **valores efímeros** (`ephemeral`) y argumentos *write-only* (1.11+) que nunca se guardan en el estado. Son la dirección del futuro para secretos.",
  "Protege el estado: backend cifrado, acceso restringido por IAM y versionado.",
 ]),

 ("h", "Estimar costes con Infracost"),
 ("code", "bash", "terminal", """infracost auth login
infracost breakdown --path .
# Name                                 Monthly Qty  Unit   Monthly Cost
# aws_instance.web
#  ├─ Instance usage (Linux, t3.micro)         730  hours        $8.32
#  └─ root_block_device: Storage (gp3)           8  GB           $0.70
# OVERALL TOTAL                                                  $9.02"""),
 ("p", "En CI, `infracost diff` puede comentar en cada Pull Request cuánto cambiará la factura."),
]

TEST = [
 ("¿Qué diferencia hay entre `postcondition` y un bloque `check`?",
  ["Ninguna", "postcondition detiene la ejecución con error; check solo muestra un aviso", "check es más antiguo", "postcondition solo funciona en outputs"], 1,
  "Las condiciones de lifecycle son bloqueantes; los check blocks son informativos."),
 ("En un `.tftest.hcl`, ¿qué hace `command = plan` en un run?",
  ["Crea los recursos", "Solo planifica, sin crear nada", "Destruye todo", "Ejecuta terraform fmt"], 1, "Rápido y gratuito, ideal para validar lógica."),
 ("¿Para qué sirve `expect_failures = [var.proyecto]`?",
  ["Para ignorar errores", "Para que el test pase solo si la validación de var.proyecto falla", "Para saltarse el test", "Para mockear la variable"], 1,
  "Así se prueba que las validaciones rechazan valores incorrectos."),
 ("¿Qué permite `mock_provider \"aws\"`?",
  ["Usar otra nube", "Ejecutar tests con apply sin llamar a AWS ni tener credenciales", "Cifrar el estado", "Simular la factura"], 1,
  "Los recursos se «crean» con valores ficticios."),
 ("`terraform validate` acepta `instance_type = \"t3.micra\"`. ¿Qué herramienta lo detecta?",
  ["terraform fmt", "TFLint con el plugin de AWS", "git", "terraform output"], 1,
  "TFLint conoce los valores válidos de cada provider."),
 ("¿Qué herramienta usarías para detectar un bucket S3 público o un disco sin cifrar?",
  ["terraform-docs", "Trivy o Checkov", "tfenv", "jq"], 1, "Son escáneres de seguridad de configuración."),
 ("¿Cuál es la forma más segura de gestionar la contraseña maestra de una base de datos RDS?",
  ["Escribirla en el .tf", "En terraform.tfvars", "manage_master_user_password = true (la genera y guarda AWS)", "En un output"], 2,
  "Así Terraform nunca conoce la contraseña y no termina en el estado."),
]

RETOS = [
 {"titulo": "Suite de tests para tu módulo de etiquetas",
  "enunciado": "Para el módulo `etiquetas` del reto del módulo 11, escribe un archivo de test con: (1) un run que compruebe que `Gestion = \"terraform\"` siempre está, (2) uno que compruebe que `extra` se combina, y (3) uno que espere fallo si `entorno` no es dev/prod (añade la validación).",
  "pista": "Accede a los outputs con `output.todas[\"Gestion\"]`.",
  "solucion": ("hcl", """# tests/etiquetas.tftest.hcl
variables {
  proyecto = "tienda"
  entorno  = "dev"
}

run "siempre_incluye_gestion" {
  command = plan
  assert {
    condition     = output.todas["Gestion"] == "terraform"
    error_message = "Falta la etiqueta Gestion"
  }
}

run "combina_extra" {
  command = plan
  variables {
    extra = { Equipo = "web" }
  }
  assert {
    condition     = output.todas["Equipo"] == "web" && output.todas["Proyecto"] == "tienda"
    error_message = "No se combinan las etiquetas extra"
  }
}

run "entorno_invalido" {
  command = plan
  variables {
    entorno = "qa"
  }
  expect_failures = [var.entorno]
}""")},
 {"titulo": "Arregla los hallazgos",
  "enunciado": "Ejecuta `trivy config .` sobre el proyecto del módulo 6 y corrige al menos dos hallazgos (por ejemplo IMDSv2 y cifrado del disco raíz). Para la regla de HTTP desde Internet, añade una excepción justificada.",
  "pista": "Busca `metadata_options` y `root_block_device { encrypted = true }` en la documentación de `aws_instance`.",
  "solucion": ("hcl", """resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  vpc_security_group_ids = [aws_security_group.web.id]

  metadata_options {
    http_tokens = "required"   # IMDSv2
  }

  root_block_device {
    encrypted = true
  }
}""")},
]
