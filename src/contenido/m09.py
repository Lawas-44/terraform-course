# -*- coding: utf-8 -*-
# Módulo 09 · El estado

LECCION = [
 ("h", "Qué es el estado"),
 ("p", "El archivo `terraform.tfstate` es la **memoria** de Terraform. Ahí apunta qué ha creado y con qué datos. Por ejemplo, que el recurso `aws_instance.web` de tu código es el servidor real `i-0123abcd` de AWS."),
 ("p", "Sin ese archivo, Terraform no sabría qué existe ya y querría crearlo todo de nuevo."),
 ("p", "Cada vez que ejecutas `plan`, Terraform compara tres cosas:"),
 ("ol", [
  "Lo que **existe de verdad** en la nube.",
  "Lo que **recuerda** (el estado).",
  "Lo que **pide tu código**.",
 ]),
 ("p", "Con esa comparación decide qué tiene que crear, cambiar o borrar."),

 ("h", "El estado guarda secretos"),
 ("p", "Así se ve una parte del archivo de estado:"),
 ("code", "json", "terraform.tfstate (fragmento)", """{
  "resources": [
    {
      "type": "random_password",
      "name": "db",
      "instances": [
        { "attributes": { "result": "x7#Kq9!mP2$vL4@n" } }
      ]
    }
  ]
}"""),
 ("warn", "La contraseña aparece **tal cual**, sin cifrar, aunque la marcaras como `sensitive`. Quien tenga el estado tiene los secretos."),
 ("p", "Reglas básicas:"),
 ("ul", [
  "No edites el estado a mano. Usa los comandos `terraform state`.",
  "No lo subas a Git ni lo envíes por correo.",
  "Si trabajas en equipo, guárdalo en un sitio compartido y seguro (módulo 10).",
 ]),

 ("h", "Cambios hechos fuera de Terraform"),
 ("p", "Si alguien cambia algo a mano (desde la web de AWS, por ejemplo), la realidad ya no coincide con el estado. A esto se le llama **drift** (deriva)."),
 ("p", "Para verlo sin cambiar nada, usa `-refresh-only`:"),
 ("term", """$ terraform plan -refresh-only

Note: Objects have changed outside of Terraform

  # aws_s3_bucket.datos has changed
  ~ resource "aws_s3_bucket" "datos" {
      ~ tags = {
          ~ "Equipo" = "plataforma" -> "datos"
        }
    }"""),
 ("p", "Ahora decides:"),
 ("table", ["Si el cambio manual...", "Haz esto"], [
  ["fue un error", "`terraform apply`: Terraform vuelve a dejarlo como dice el código"],
  ["es correcto", "Cambia también tu código para que coincida"],
 ]),

 ("h", "Comandos para ver el estado"),
 ("term", """$ terraform state list
aws_s3_bucket.datos
random_password.db
$ terraform state show aws_s3_bucket.datos
$ terraform show"""),
 ("table", ["Comando", "Qué hace"], [
  ["`terraform state list`", "Lista todo lo que Terraform recuerda"],
  ["`terraform state show NOMBRE`", "Muestra los datos de un recurso"],
  ["`terraform show`", "Muestra todo el estado de forma legible"],
 ]),

 ("h", "Cambiar el nombre de un recurso"),
 ("p", "Si cambias el nombre de un recurso en el código (por ejemplo de `aws_s3_bucket.viejo` a `aws_s3_bucket.nuevo`), Terraform pensará que es otro recurso: borrará el viejo y creará uno nuevo. Para evitarlo, díselo:"),
 ("term", """$ terraform state mv aws_s3_bucket.viejo aws_s3_bucket.nuevo
Successfully moved 1 object(s).
$ terraform plan
No changes."""),
 ("tip", "En el módulo 12 verás el bloque `moved`, que hace lo mismo desde el código."),

 ("h", "Olvidar un recurso sin borrarlo"),
 ("p", "`terraform state rm` hace que Terraform deje de gestionar un recurso. **El recurso no se borra**: sigue existiendo en la nube, pero Terraform ya no lo recuerda."),
 ("term", """$ terraform state rm aws_s3_bucket.datos
Removed aws_s3_bucket.datos"""),
 ("warn", "Si pierdes el archivo de estado, Terraform olvida todo, pero los recursos siguen existiendo y cobrando. Haz copias o, mejor, guárdalo en un sitio seguro (módulo 10)."),
 ("term", """$ terraform state pull > copia-estado.tfstate"""),
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
