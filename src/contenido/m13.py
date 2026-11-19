# -*- coding: utf-8 -*-
# Módulo 13 · Validación, testing y seguridad

LECCION = [
 ("h", "Detectar errores pronto"),
 ("p", "Cuanto antes encuentres un error, más fácil es arreglarlo. Terraform y otras herramientas te ayudan en cada momento:"),
 ("table", ["Herramienta", "Qué detecta"], [
  ["`terraform validate`", "Errores al escribir el código"],
  ["`validation` en variables", "Valores de entrada incorrectos"],
  ["`precondition` y `postcondition`", "Que se cumplan condiciones antes y después de crear algo"],
  ["Bloques `check`", "Avisos sobre el estado de la infraestructura"],
  ["`terraform test`", "Que tu código hace lo que esperas"],
  ["TFLint", "Valores que no existen y malas prácticas"],
  ["Trivy y Checkov", "Configuraciones inseguras"],
 ]),

 ("h", "Condiciones antes y después"),
 ("p", "Dentro de `lifecycle` puedes poner condiciones que deben cumplirse. Si no se cumplen, Terraform se para con un error:"),
 ("code", "hcl", "condiciones", """resource "aws_instance" "web" {
  ami           = data.aws_ami.elegida.id
  instance_type = "t3.micro"

  lifecycle {
    # Se comprueba ANTES de crear
    precondition {
      condition     = data.aws_ami.elegida.architecture == "x86_64"
      error_message = "La imagen debe ser x86_64."
    }

    # Se comprueba DESPUÉS de crear (self es el propio recurso)
    postcondition {
      condition     = self.public_ip != ""
      error_message = "El servidor debería tener IP pública."
    }
  }
}"""),

 ("h", "Bloques check: avisos"),
 ("p", "Un bloque `check` comprueba algo pero **no para** el proceso: solo muestra un aviso. Por ejemplo, que la web responda:"),
 ("code", "hcl", "check.tf", """check "web_responde" {
  data "http" "home" {
    url = "http://${aws_instance.web.public_ip}"
  }

  assert {
    condition     = data.http.home.status_code == 200
    error_message = "La web no responde correctamente."
  }
}"""),

 ("h", "Tests con terraform test"),
 ("p", "Terraform tiene su propio sistema de pruebas. Los tests se escriben en archivos que terminan en `.tftest.hcl`, normalmente en una carpeta `tests/`. Este es el código que vamos a probar:"),
 ("code", "hcl", "main.tf", """variable "proyecto" {
  type = string
  validation {
    condition     = length(var.proyecto) >= 3
    error_message = "Mínimo 3 letras."
  }
}

variable "entorno" {
  type    = string
  default = "dev"
}

output "prefijo" {
  value = "${var.proyecto}-${var.entorno}"
}"""),
 ("p", "Y estos son los tests. Cada bloque `run` es una prueba:"),
 ("code", "hcl", "tests/prefijo.tftest.hcl", """variables {
  proyecto = "tienda"
}

run "prefijo_por_defecto" {
  command = plan

  assert {
    condition     = output.prefijo == "tienda-dev"
    error_message = "El prefijo debería ser tienda-dev"
  }
}

run "rechaza_nombres_cortos" {
  command = plan

  variables {
    proyecto = "ab"
  }

  # Esta prueba pasa si la validación FALLA
  expect_failures = [var.proyecto]
}"""),
 ("ul", [
  "`command = plan`: solo planifica, no crea nada. Rápido y gratis.",
  "`command = apply`: crea los recursos de verdad y los borra al terminar.",
  "`assert`: lo que debe cumplirse.",
  "`expect_failures`: sirve para comprobar que un valor incorrecto se rechaza.",
 ]),
 ("term", """$ terraform test
tests/prefijo.tftest.hcl... in progress
  run "prefijo_por_defecto"... pass
  run "rechaza_nombres_cortos"... pass
tests/prefijo.tftest.hcl... pass

Success! 2 passed, 0 failed."""),
 ("p", "Para probar código de AWS sin crear nada ni pagar, puedes simular el provider con `mock_provider`. Terraform inventa los datos en lugar de llamar a AWS:"),
 ("code", "hcl", "tests/bucket.tftest.hcl", """mock_provider "aws" {}

run "crea_bucket" {
  command = apply

  assert {
    condition     = aws_s3_object.index.content_type == "text/html"
    error_message = "La página debe ser text/html"
  }
}"""),

 ("h", "TFLint: detectar valores que no existen"),
 ("p", "`terraform validate` no sabe que `t3.micra` no existe; para él es solo un texto. **TFLint** sí lo sabe:"),
 ("term", """$ tflint --init
$ tflint
Error: "t3.micra" is an invalid value as instance_type"""),

 ("h", "Trivy y Checkov: seguridad"),
 ("p", "Estas herramientas revisan tu código y te avisan de problemas de seguridad: buckets públicos, discos sin cifrar, puertos abiertos a todo Internet..."),
 ("term", """$ trivy config .
HIGH: Security group rule allows ingress from public internet.
  main.tf:15
$ checkov -d ."""),
 ("p", "No todos los avisos son errores: una web pública **tiene** que estar abierta a Internet. Si aceptas un aviso, deja un comentario explicando por qué."),

 ("h", "Comprobar todo antes de cada commit"),
 ("p", "La herramienta **pre-commit** ejecuta estas comprobaciones solas cada vez que haces `git commit`:"),
 ("code", "yaml", ".pre-commit-config.yaml", """repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.96.1
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_tflint"""),
 ("term", """$ pip install pre-commit
$ pre-commit install"""),

 ("h", "Contraseñas y secretos"),
 ("ul", [
  "Nunca escribas contraseñas en los archivos `.tf` ni en `.tfvars` que subas a Git.",
  "Pásalas con variables de entorno (`TF_VAR_password`) y márcalas como `sensitive`.",
  "Mejor todavía: deja que AWS cree y guarde la contraseña. Así Terraform nunca la conoce:",
 ]),
 ("code", "hcl", "contraseña gestionada por AWS", """resource "aws_db_instance" "app" {
  engine              = "postgres"
  instance_class      = "db.t4g.micro"
  allocated_storage   = 20
  username            = "app"
  skip_final_snapshot = true

  manage_master_user_password = true   # AWS genera y guarda la contraseña
}"""),
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
