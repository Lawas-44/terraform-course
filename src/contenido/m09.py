# -*- coding: utf-8 -*-
# Módulo 09 · El estado

LECCION = [
 ("h", "Para qué sirve el estado"),
 ("p", "El archivo `terraform.tfstate` es la **memoria** de Terraform. Cumple cuatro funciones:"),
 ("ol", [
  "**Mapear código ↔ realidad**: sabe que `aws_instance.web` es la instancia `i-0123abcd`. Sin esto no podría saber qué recurso real corresponde a cada bloque.",
  "**Guardar metadatos**: dependencias entre recursos, para poder destruir en el orden correcto aunque ya hayas borrado el código.",
  "**Rendimiento**: guarda los atributos para no tener que preguntar todo a la API en cada operación (en proyectos grandes, miles de llamadas).",
  "**Detectar cambios**: comparando estado, código y realidad sabe qué ha cambiado y quién lo cambió.",
 ]),
 ("p", "En cada `plan` Terraform hace tres comparaciones:"),
 ("code", "text", "cómo calcula un plan", """             1. refresh                     2. diff
  REALIDAD  ───────────────►  ESTADO  ◄──────────────────  CÓDIGO
 (API AWS)   actualiza el     (tfstate)  ¿qué hay que cambiar   (.tf)
             estado con lo               para que el estado
             que hay de verdad           sea igual que el código?"""),

 ("h", "Por dentro del archivo de estado"),
 ("p", "Crea algo sencillo y abre el estado. Son unos pocos campos importantes:"),
 ("code", "json", "terraform.tfstate", """{
  "version": 4,
  "terraform_version": "1.10.5",
  "serial": 7,
  "lineage": "8a6b0c2e-1f3d-4e5a-9b7c-6d8e0f1a2b3c",
  "outputs": { ... },
  "resources": [
    {
      "mode": "managed",
      "type": "random_password",
      "name": "db",
      "provider": "provider[\\"registry.terraform.io/hashicorp/random\\"]",
      "instances": [
        {
          "attributes": {
            "length": 16,
            "result": "x7#Kq9!mP2$vL4@n"
          },
          "sensitive_attributes": [ ... ]
        }
      ]
    }
  ]
}"""),
 ("table", ["Campo", "Significado"], [
  ["`serial`", "Se incrementa en cada cambio del estado"],
  ["`lineage`", "Identificador único de este estado desde su creación (evita mezclar estados distintos)"],
  ["`mode`", "`managed` (resource) o `data` (data source)"],
  ["`attributes`", "Todos los atributos del recurso… **incluidos los secretos**"],
 ]),
 ("warn", "Fíjate en `\"result\": \"x7#Kq9!mP2$vL4@n\"`: la contraseña está **en texto plano**, aunque la marcaras como `sensitive`. Quien tenga acceso al estado tiene acceso a todos los secretos que gestiona Terraform."),
 ("p", "Reglas de oro del estado:"),
 ("ul", [
  "**Nunca** lo edites a mano. Usa los comandos `terraform state`.",
  "**Nunca** lo subas a Git ni lo compartas por email/chat.",
  "En equipo, siempre en un **backend remoto** cifrado, con versionado y bloqueo (módulo 10).",
  "Terraform guarda la versión anterior en `terraform.tfstate.backup` (solo en estado local).",
 ]),

 ("h", "Drift: cuando la realidad cambia por su cuenta"),
 ("p", "El **drift** (deriva) ocurre cuando alguien modifica la infraestructura fuera de Terraform: desde la consola web, con la CLI, con un script… Vamos a provocarlo:"),
 ("code", "hcl", "main.tf", """resource "aws_s3_bucket" "drift" {
  bucket_prefix = "curso-drift-"
  force_destroy = true

  tags = {
    Equipo = "plataforma"
  }
}

output "bucket" {
  value = aws_s3_bucket.drift.bucket
}"""),
 ("p", "Aplica, y después cambia la etiqueta `Equipo` a `datos` **desde la consola de AWS** (o con la CLI):"),
 ("code", "bash", "provocar drift", """aws s3api put-bucket-tagging --bucket $(terraform output -raw bucket) \\
  --tagging 'TagSet=[{Key=Equipo,Value=datos}]'"""),
 ("p", "Ahora tienes dos opciones para ver qué ha pasado:"),
 ("term", """$ terraform plan -refresh-only

Note: Objects have changed outside of Terraform

Terraform detected the following changes made outside of Terraform since the
last "terraform apply":

  # aws_s3_bucket.drift has changed
  ~ resource "aws_s3_bucket" "drift" {
      ~ tags = {
          ~ "Equipo" = "plataforma" -> "datos"
        }
    }

This is a refresh-only plan, so Terraform will not take any actions to undo
these. If you were expecting these changes then you can apply this plan to
record the updated values in the Terraform state without changing any remote
objects."""),
 ("p", "Y decidir:"),
 ("table", ["Si el cambio manual…", "Haz esto", "Resultado"], [
  ["Era un error", "`terraform apply`", "Terraform **revierte** la realidad a lo que dice el código"],
  ["Era correcto y quieres conservarlo", "Actualiza el código (`Equipo = \"datos\"`) y `terraform plan` → sin cambios", "Código y realidad vuelven a coincidir"],
  ["Solo quieres que el estado lo refleje", "`terraform apply -refresh-only`", "Actualiza el estado sin tocar la infraestructura (el siguiente `plan` querrá revertirlo si el código no cambia)"],
 ]),
 ("info", "`terraform refresh` (a secas) está obsoleto porque actualizaba el estado sin enseñarte nada. Usa `apply -refresh-only`, que te muestra los cambios y pide confirmación."),

 ("h", "Comandos de estado"),
 ("p", "Los subcomandos de `terraform state` permiten consultar y reorganizar el estado de forma segura:"),
 ("code", "bash", "consultar", """terraform state list                       # todos los recursos
terraform state list 'aws_s3_bucket.*'     # filtrar
terraform state show aws_s3_bucket.drift   # atributos de uno
terraform show                             # todo el estado legible
terraform show -json | jq '.values.root_module.resources[].address'"""),
 ("p", "**Mover/renombrar** un recurso: has cambiado el nombre en el código de `aws_s3_bucket.drift` a `aws_s3_bucket.datos`. Sin hacer nada, Terraform destruiría el viejo y crearía uno nuevo. Con `state mv` le dices que es el mismo:"),
 ("code", "bash", "renombrar", """terraform state mv aws_s3_bucket.drift aws_s3_bucket.datos
# Move "aws_s3_bucket.drift" to "aws_s3_bucket.datos"
# Successfully moved 1 object(s).
terraform plan   # No changes."""),
 ("tip", "Desde Terraform 1.1 hay una forma mejor y declarativa de hacer esto: el bloque `moved`, que queda en el código y funciona para todo el equipo. Lo verás en el módulo 12."),
 ("p", "**Dejar de gestionar** un recurso sin borrarlo (por ejemplo, porque lo va a gestionar otro equipo):"),
 ("code", "bash", "olvidar", """terraform state rm aws_s3_bucket.datos
# Removed aws_s3_bucket.datos
# El bucket SIGUE EXISTIENDO en AWS. Terraform simplemente lo olvida.
# Si no quitas también el bloque del código, el próximo plan intentará crearlo."""),
 ("p", "**Copias de seguridad** manuales antes de operaciones delicadas:"),
 ("code", "bash", "backup", """terraform state pull > backup-$(date +%Y%m%d-%H%M).tfstate
# ...operación delicada...
# Si algo sale mal (último recurso):
terraform state push backup-20261119-1030.tfstate"""),
 ("warn", "`state push` sobrescribe el estado. Úsalo solo en emergencias y nunca con un estado de otro proyecto (Terraform lo impide comparando el `lineage`, salvo con `-force`)."),

 ("h", "¿Qué pasa si pierdo el estado?"),
 ("p", "Si borras `terraform.tfstate` (y su backup), Terraform «olvida» todo. Los recursos siguen existiendo (¡y cobrando!), pero el siguiente `plan` querrá crearlos de nuevo, provocando errores de nombre duplicado o recursos repetidos. La solución sería **importarlos** uno a uno (módulo 12). Por eso el estado se guarda en un backend remoto con versionado."),
]

TEST = [
 ("¿Cuál NO es una función del estado?",
  ["Mapear recursos del código con objetos reales", "Guardar dependencias", "Guardar el código fuente .tf", "Mejorar el rendimiento"], 2,
  "El código vive en los .tf; el estado guarda información sobre los recursos reales."),
 ("Una contraseña generada con `random_password` y marcada sensitive…",
  ["no se guarda en el estado", "se guarda cifrada", "se guarda en texto plano en el estado", "se guarda en AWS"], 2,
  "Por eso el estado debe protegerse como un secreto."),
 ("¿Qué es el drift?",
  ["Un error de sintaxis", "Diferencias entre la realidad y el estado causadas por cambios fuera de Terraform", "Un tipo de backend", "Una versión del provider"], 1,
  "Ocurre cuando alguien modifica recursos manualmente o con otras herramientas."),
 ("¿Qué comando muestra el drift sin proponer cambios en la infraestructura?",
  ["terraform plan -refresh-only", "terraform refresh", "terraform validate", "terraform show"], 0,
  "Enseña solo qué ha cambiado fuera de Terraform."),
 ("¿Qué hace `terraform state rm aws_instance.web`?",
  ["Destruye la instancia", "Quita la instancia del estado sin destruirla", "Recrea la instancia", "Borra el código"], 1,
  "El recurso sigue existiendo; Terraform deja de gestionarlo."),
 ("Has renombrado un recurso en el código. ¿Qué evitas con `terraform state mv`?",
  ["Que se formatee", "Que Terraform lo destruya y lo vuelva a crear", "Que se cifre", "Nada"], 1,
  "Le indicas que el recurso con el nombre nuevo es el mismo objeto real."),
]

RETOS = [
 {"titulo": "Detective de drift",
  "enunciado": "Crea un `local_file` y luego edita a mano su contenido (con tu editor). ¿Qué muestra `terraform plan -refresh-only`? ¿Y `terraform plan`? Explica la diferencia.",
  "pista": "El provider local detecta si el contenido del archivo ha cambiado.",
  "solucion": ("text", """plan -refresh-only → informa de que local_file ya no existe tal como estaba
                      (el provider lo detecta por el hash del contenido) y
                      propone actualizar el estado.

plan                → propone RECREAR el archivo (+ create) con el contenido
                      del código, deshaciendo tu edición manual.

Diferencia: -refresh-only solo sincroniza el estado con la realidad;
plan normal intenta que la realidad vuelva a ser igual que el código.""")},
 {"titulo": "Renombrado seguro",
  "enunciado": "Tienes `random_pet.mascota` en el estado. Renómbralo en el código a `random_pet.animal` y consigue que `terraform plan` diga *No changes*. Hazlo primero con `terraform state mv` y, tras deshacerlo, con un bloque `moved`.",
  "pista": "El bloque `moved` tiene `from` y `to`.",
  "solucion": ("hcl", """# Opción 1 (imperativa):
#   terraform state mv random_pet.mascota random_pet.animal

# Opción 2 (declarativa, recomendada):
resource "random_pet" "animal" {}

moved {
  from = random_pet.mascota
  to   = random_pet.animal
}""")},
]
