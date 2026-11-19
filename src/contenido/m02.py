# -*- coding: utf-8 -*-
# Módulo 02 · Tu primer proyecto

LECCION = [
 ("h", "Un proyecto = una carpeta"),
 ("p", "En Terraform, un proyecto es simplemente **una carpeta con archivos `.tf`**. Cuando ejecutas un comando, Terraform lee *todos* los `.tf` de la carpeta actual (no las subcarpetas) y los trata como una sola configuración. A esa carpeta se le llama **root module** (módulo raíz)."),
 ("p", "Para aprender el flujo sin gastar dinero ni configurar cuentas usaremos dos providers que funcionan en tu ordenador:"),
 ("ul", [
  "`hashicorp/random`: genera valores aleatorios (nombres, contraseñas, números).",
  "`hashicorp/local`: crea archivos en tu disco.",
 ]),
 ("code", "bash", "terminal", """mkdir -p ~/terraform-labs/02-primer-proyecto
cd ~/terraform-labs/02-primer-proyecto
code main.tf"""),

 ("h", "Escribe tu primera configuración"),
 ("p", "Copia esto en `main.tf`. Debajo lo explicamos bloque a bloque:"),
 ("code", "hcl", "main.tf", """terraform {
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
 ("ul", [
  "**`terraform { ... }`**: ajustes del propio Terraform. Aquí exigimos versión 1.6 o superior y declaramos qué providers usamos, de dónde salen (`source`) y qué versiones aceptamos.",
  "**`resource \"random_pet\" \"nombre\"`**: un recurso. `random_pet` es el *tipo* (lo aporta el provider random) y `nombre` es el *nombre local* que tú eliges para referirte a él. Genera algo como `gentle-turtle`.",
  "**`resource \"local_file\" \"saludo\"`**: un archivo en disco. Fíjate en `${random_pet.nombre.id}`: estamos **usando el resultado de otro recurso**. Eso crea una dependencia: Terraform sabe que primero debe generar el nombre.",
  "**`path.module`**: la ruta de la carpeta actual.",
  "**`output`**: un valor que Terraform mostrará al terminar.",
 ]),

 ("h", "terraform init: preparar la carpeta"),
 ("p", "El primer comando en cualquier proyecto nuevo (o cuando añades providers o módulos) es `init`:"),
 ("term", """$ terraform init

Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/local versions matching "~> 2.5"...
- Finding hashicorp/random versions matching "~> 3.6"...
- Installing hashicorp/local v2.5.2...
- Installing hashicorp/random v3.6.3...

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above.

Terraform has been successfully initialized!"""),
 ("p", "Mira qué ha aparecido en la carpeta:"),
 ("code", "text", "estructura", """02-primer-proyecto/
├── .terraform/            ← plugins descargados (no va a Git)
│   └── providers/...
├── .terraform.lock.hcl    ← versiones y hashes exactos (sí va a Git)
└── main.tf"""),
 ("tip", "`init` es seguro: nunca crea ni borra infraestructura. Puedes ejecutarlo tantas veces como quieras."),

 ("h", "terraform plan: ver antes de tocar"),
 ("p", "`plan` compara tu código con lo que existe y te enseña qué haría. **No cambia nada.** Es la red de seguridad más importante de Terraform: acostúmbrate a leerlo siempre."),
 ("term", """$ terraform plan

Terraform used the selected providers to generate the following execution
plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # local_file.saludo will be created
  + resource "local_file" "saludo" {
      + content              = (known after apply)
      + filename             = "./saludo.txt"
      + id                   = (known after apply)
      ...
    }

  # random_pet.nombre will be created
  + resource "random_pet" "nombre" {
      + id        = (known after apply)
      + length    = 2
      + separator = "-"
    }

Plan: 2 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + nombre_mascota = (known after apply)"""),
 ("p", "Cómo se lee un plan:"),
 ("table", ["Símbolo", "Significado"], [
  ["`+`", "Se va a **crear**"],
  ["`-`", "Se va a **destruir**"],
  ["`~`", "Se va a **modificar** sin recrear (*update in-place*)"],
  ["`-/+`", "Se va a **destruir y volver a crear** (reemplazo)"],
  ["`<=`", "Se va a **leer** (data source)"],
  ["`(known after apply)`", "El valor aún no se conoce; lo sabremos al crear el recurso"],
 ]),

 ("h", "terraform apply: hacerlo realidad"),
 ("p", "`apply` vuelve a calcular el plan, te lo enseña y **pide confirmación**. Solo se ejecuta si escribes exactamente `yes`:"),
 ("term", """$ terraform apply
...
Plan: 2 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

random_pet.nombre: Creating...
random_pet.nombre: Creation complete after 0s [id=gentle-turtle]
local_file.saludo: Creating...
local_file.saludo: Creation complete after 0s [id=3f1e...]

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

Outputs:

nombre_mascota = "gentle-turtle"

$ cat saludo.txt
¡Hola, gentle-turtle! Este archivo lo creó Terraform."""),
 ("p", "Observa el orden: primero `random_pet`, después `local_file`. Terraform lo dedujo solo gracias a la referencia `random_pet.nombre.id`."),
 ("p", "Ahora ejecuta `terraform apply` **otra vez**:"),
 ("term", """$ terraform apply
random_pet.nombre: Refreshing state... [id=gentle-turtle]
local_file.saludo: Refreshing state... [id=3f1e...]

No changes. Your infrastructure matches the configuration."""),
 ("p", "¡Idempotencia en acción! Como todo coincide con el código, no hace nada."),
 ("warn", "Existe `terraform apply -auto-approve`, que no pide confirmación. Evítalo mientras aprendes: leer el plan antes de escribir `yes` es lo que te salvará de borrar algo importante."),

 ("h", "El estado: la memoria de Terraform"),
 ("p", "Tras el `apply` ha aparecido un archivo nuevo: `terraform.tfstate`. Ábrelo (sin modificarlo):"),
 ("code", "json", "terraform.tfstate (fragmento)", """{
  "version": 4,
  "terraform_version": "1.10.5",
  "serial": 3,
  "resources": [
    {
      "mode": "managed",
      "type": "random_pet",
      "name": "nombre",
      "instances": [
        { "attributes": { "id": "gentle-turtle", "length": 2, "separator": "-" } }
      ]
    }
  ]
}"""),
 ("p", "Así es como Terraform sabe que `random_pet.nombre` en tu código corresponde a la mascota `gentle-turtle`. Si no existiera el estado, Terraform pensaría que tiene que crearlo todo de nuevo. Lo estudiaremos a fondo en el módulo 9."),
 ("code", "bash", "comandos para inspeccionar", """terraform state list           # qué recursos gestiona
terraform show                 # el estado en formato legible
terraform output nombre_mascota"""),

 ("h", "Cambios: actualizar vs reemplazar"),
 ("p", "Cambia `length = 2` por `length = 3` y ejecuta `terraform plan`:"),
 ("term", """  # local_file.saludo must be replaced
-/+ resource "local_file" "saludo" {
      ~ content  = <<-EOT # forces replacement
          - ¡Hola, gentle-turtle! Este archivo lo creó Terraform.
          + (known after apply)
        EOT
      ...
    }

  # random_pet.nombre must be replaced
-/+ resource "random_pet" "nombre" {
      ~ id        = "gentle-turtle" -> (known after apply)
      ~ length    = 2 -> 3 # forces replacement
        # (1 unchanged attribute hidden)
    }

Plan: 2 to add, 0 to change, 2 to destroy."""),
 ("p", "Fíjate en `# forces replacement`: algunos argumentos no se pueden cambiar sobre la marcha y obligan a **recrear** el recurso. Con un archivo no importa, pero con un servidor o una base de datos significa perder lo que había dentro. **Por eso siempre se lee el plan.** Además, como el archivo depende del nombre, también se recrea: los cambios se propagan por las dependencias."),
 ("p", "Otro experimento: borra a mano `saludo.txt` (`rm saludo.txt`) y ejecuta `terraform plan`. Terraform detecta que falta y propone crearlo de nuevo. Ha comparado el estado con la realidad."),

 ("h", "terraform destroy: limpiar"),
 ("p", "`destroy` elimina **todo** lo que gestiona la configuración. También muestra un plan (con `-`) y pide confirmación:"),
 ("term", """$ terraform destroy
...
Plan: 0 to add, 0 to change, 2 to destroy.

  Enter a value: yes

local_file.saludo: Destroying...
random_pet.nombre: Destroying...
Destroy complete! Resources: 2 destroyed."""),
 ("p", "El orden ahora es el inverso: primero lo que depende (el archivo), luego aquello de lo que depende (el nombre)."),
 ("info", "Resumen del flujo: `init` (una vez) → `plan` → `apply` → … cambios … → `plan` → `apply` → `destroy` al terminar."),
]

TEST = [
 ("¿Qué hace `terraform init`?",
  ["Crea los recursos", "Descarga providers/módulos y prepara la carpeta", "Borra el estado", "Formatea el código"], 1,
  "`init` prepara el directorio: backend, providers y módulos. Nunca toca la infraestructura."),
 ("En un plan, ¿qué indica el símbolo `-/+`?",
  ["El recurso se crea", "El recurso se modifica en sitio", "El recurso se destruye y se vuelve a crear", "Hay un error"], 2,
  "Es un reemplazo: algún argumento marcado como *forces replacement* ha cambiado."),
 ("Ejecutas `terraform apply` dos veces seguidas sin tocar el código. ¿Qué pasa la segunda vez?",
  ["Crea los recursos por duplicado", "Da error", "No hace cambios: la infraestructura ya coincide", "Destruye todo"], 2,
  "Terraform es idempotente: si el estado y la realidad coinciden con el código, no hay nada que hacer."),
 ("¿Cómo sabe Terraform que debe crear `random_pet` antes que `local_file`?",
  ["Por el orden en el archivo", "Por orden alfabético", "Porque `local_file` hace referencia a `random_pet.nombre.id`", "Lo elige al azar"], 2,
  "Las referencias crean dependencias implícitas; el orden en el archivo no importa."),
 ("¿Qué archivo usa Terraform para recordar qué recursos ha creado?",
  ["main.tf", ".terraform.lock.hcl", "terraform.tfstate", ".gitignore"], 2,
  "El estado mapea cada recurso del código con el objeto real que existe."),
 ("¿Qué significa `(known after apply)`?",
  ["Que hay un error", "Que el valor solo se conocerá cuando se cree el recurso", "Que el valor es secreto", "Que el recurso ya existe"], 1,
  "Valores como IDs o IPs los genera el proveedor al crear el recurso."),
]

RETOS = [
 {"titulo": "Tres archivos encadenados",
  "enunciado": "Añade un segundo `random_pet` llamado `apellido` y un archivo `presentacion.txt` cuyo contenido sea «Me llamo NOMBRE APELLIDO». Añade un output con el texto completo.",
  "pista": "Puedes usar dos interpolaciones en el mismo string: `\"${a} ${b}\"`.",
  "solucion": ("hcl", """resource "random_pet" "apellido" {
  length = 1
}

resource "local_file" "presentacion" {
  filename = "${path.module}/presentacion.txt"
  content  = "Me llamo ${random_pet.nombre.id} ${random_pet.apellido.id}\\n"
}

output "presentacion" {
  value = local_file.presentacion.content
}""")},
 {"titulo": "Una contraseña aleatoria",
  "enunciado": "Usa el recurso `random_password` (del mismo provider random) para generar una contraseña de 16 caracteres y muéstrala en un output. ¿Qué ocurre al hacer `apply`?",
  "pista": "Busca `random_password` en registry.terraform.io. Fíjate en el atributo `result`.",
  "solucion": ("hcl", """resource "random_password" "db" {
  length  = 16
  special = true
}

output "password" {
  value     = random_password.db.result
  sensitive = true # obligatorio: el atributo es sensible
}

# Terraform muestra password = <sensitive>.
# Para verla: terraform output -raw password
# Ojo: está guardada en texto plano en terraform.tfstate.""")},
]
