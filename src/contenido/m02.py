# -*- coding: utf-8 -*-
# Módulo 02 · Tu primer proyecto

LECCION = [
 ("h", "Un proyecto es una carpeta"),
 ("p", "Un proyecto de Terraform es una **carpeta con archivos que terminan en `.tf`**. Terraform lee todos los `.tf` de la carpeta en la que estás."),
 ("p", "Para practicar sin gastar dinero usaremos dos providers que funcionan en tu ordenador, sin nube:"),
 ("ul", [
  "`random`: inventa valores al azar (nombres, números, contraseñas).",
  "`local`: crea archivos en tu ordenador.",
 ]),
 ("term", """$ mkdir 02-primer-proyecto
$ cd 02-primer-proyecto
$ code main.tf"""),

 ("h", "Tu primer archivo"),
 ("p", "Copia esto en `main.tf`:"),
 ("code", "hcl", "main.tf", """terraform {
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
  content  = "Hola, ${random_pet.nombre.id}! Este archivo lo creó Terraform.\\n"
}

output "nombre_mascota" {
  value = random_pet.nombre.id
}"""),
 ("p", "Qué significa cada parte:"),
 ("ul", [
  "**`terraform { ... }`**: indica qué providers necesitamos y qué versión.",
  "**`resource \"random_pet\" \"nombre\"`**: pide un nombre de mascota al azar (por ejemplo, `gentle-turtle`). `random_pet` es el tipo y `nombre` es el nombre que le damos nosotros.",
  "**`resource \"local_file\" \"saludo\"`**: crea el archivo `saludo.txt`. Dentro usa el nombre de la mascota con `${random_pet.nombre.id}`.",
  "**`output`**: muestra un valor en la terminal al terminar.",
 ]),

 ("h", "Paso 1: terraform init"),
 ("p", "`init` prepara la carpeta y descarga los providers. Se ejecuta una vez al empezar (y cuando añades un provider nuevo):"),
 ("term", """$ terraform init
Initializing provider plugins...
- Installing hashicorp/local v2.5.2...
- Installing hashicorp/random v3.6.3...

Terraform has been successfully initialized!"""),
 ("p", "Aparecen dos cosas nuevas en la carpeta: la carpeta `.terraform/` (los providers descargados) y el archivo `.terraform.lock.hcl` (las versiones exactas)."),

 ("h", "Paso 2: terraform plan"),
 ("p", "`plan` te enseña lo que Terraform **va a hacer**, pero **no hace nada todavía**. Léelo siempre antes de aplicar:"),
 ("term", """$ terraform plan

  # local_file.saludo will be created
  + resource "local_file" "saludo" {
      + filename = "./saludo.txt"
      ...
    }

  # random_pet.nombre will be created
  + resource "random_pet" "nombre" {
      + id     = (known after apply)
      + length = 2
    }

Plan: 2 to add, 0 to change, 0 to destroy."""),
 ("p", "Los símbolos del plan:"),
 ("table", ["Símbolo", "Significado"], [
  ["`+`", "Se va a crear"],
  ["`~`", "Se va a modificar"],
  ["`-`", "Se va a borrar"],
  ["`-/+`", "Se va a borrar y crear de nuevo"],
  ["`(known after apply)`", "El valor se conocerá al crearlo"],
 ]),

 ("h", "Paso 3: terraform apply"),
 ("p", "`apply` hace los cambios. Antes te enseña el plan y te pide que escribas `yes` para confirmar:"),
 ("term", """$ terraform apply
...
Plan: 2 to add, 0 to change, 0 to destroy.

  Enter a value: yes

random_pet.nombre: Creation complete after 0s [id=gentle-turtle]
local_file.saludo: Creation complete after 0s

Apply complete! Resources: 2 added, 0 changed, 0 destroyed.

Outputs:
nombre_mascota = "gentle-turtle"

$ cat saludo.txt
Hola, gentle-turtle! Este archivo lo creó Terraform."""),
 ("p", "Fíjate: primero creó el nombre y después el archivo. Terraform se dio cuenta solo de que el archivo necesita el nombre."),
 ("p", "Si ejecutas `terraform apply` otra vez, no hace nada, porque todo está ya como pide el código:"),
 ("term", """$ terraform apply
No changes. Your infrastructure matches the configuration."""),

 ("h", "El archivo de estado"),
 ("p", "Después del `apply` aparece el archivo `terraform.tfstate`. Ahí Terraform apunta lo que ha creado. Así sabe, la próxima vez, qué existe ya."),
 ("warn", "No edites ni borres este archivo. Lo veremos con calma en el módulo 9."),

 ("h", "Hacer un cambio"),
 ("p", "Cambia `length = 2` por `length = 3` y ejecuta `terraform plan`:"),
 ("term", """$ terraform plan
-/+ resource "random_pet" "nombre" {
      ~ length = 2 -> 3 # forces replacement
    }
-/+ resource "local_file" "saludo" { ... }

Plan: 2 to add, 0 to change, 2 to destroy."""),
 ("p", "Algunos cambios no se pueden hacer «en caliente» y obligan a **borrar y crear de nuevo** (`forces replacement`). Con un archivo no pasa nada, pero con un servidor perderías lo que tuviera dentro. Por eso hay que leer el plan."),

 ("h", "Paso 4: terraform destroy"),
 ("p", "`destroy` borra todo lo que ha creado este proyecto. También pide confirmación:"),
 ("term", """$ terraform destroy
...
Plan: 0 to add, 0 to change, 2 to destroy.

  Enter a value: yes

Destroy complete! Resources: 2 destroyed."""),
 ("info", "Resumen: `init` una vez, luego `plan` y `apply` cada vez que cambies algo, y `destroy` al terminar."),
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


PROYECTO = {'titulo': 'Inicializa la carpeta de Terraform',
 'bloques': [('p',
              'Crea el archivo con las versiones y los providers que usará el proyecto: `aws` para crear los '
              'servidores y `local` para escribir archivos (lo usarás en el paso del módulo 8).'),
             ('code',
              'hcl',
              'terraform/versions.tf',
              'terraform {\n'
              '  required_version = ">= 1.10"\n'
              '\n'
              '  required_providers {\n'
              '    aws = {\n'
              '      source  = "hashicorp/aws"\n'
              '      version = "~> 6.0"\n'
              '    }\n'
              '    local = {\n'
              '      source  = "hashicorp/local"\n'
              '      version = "~> 2.5"\n'
              '    }\n'
              '  }\n'
              '}'),
             ('term',
              '$ cd terraform\n'
              '$ terraform init\n'
              'Initializing provider plugins...\n'
              '- Installing hashicorp/aws v6.4.0...\n'
              '- Installing hashicorp/local v2.5.2...\n'
              '\n'
              'Terraform has been successfully initialized!'),
             ('p', 'Sube el lock file a Git (no la carpeta `.terraform/`, que ya está en el `.gitignore`):'),
             ('term', '$ git add versions.tf .terraform.lock.hcl\n$ git commit -m "Inicializa Terraform"'),
             ('p', 'Resultado de este paso: la carpeta `terraform/` está preparada.')]}
