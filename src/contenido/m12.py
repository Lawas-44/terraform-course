# -*- coding: utf-8 -*-
# Módulo 12 · Importar y refactorizar

LECCION = [
 ("h", "El escenario: infraestructura creada a mano"),
 ("p", "Es lo más habitual al llegar a una empresa: hay recursos creados desde la consola hace años y quieren pasarlos a Terraform. No hace falta destruirlos y recrearlos: se pueden **importar**, es decir, decirle a Terraform «este recurso que ya existe corresponde a este bloque de mi código»."),
 ("p", "Para practicar, crea a mano un bucket y un security group:"),
 ("code", "bash", "crear recursos «a mano»", """aws s3api create-bucket --bucket legado-$(aws sts get-caller-identity --query Account --output text) \\
  --region eu-west-1 --create-bucket-configuration LocationConstraint=eu-west-1

aws ec2 create-security-group --group-name legado-sg --description "Creado a mano"
# { "GroupId": "sg-0abc123def4567890" }"""),

 ("h", "El bloque import (Terraform 1.5+)"),
 ("p", "La forma moderna es **declarativa**: escribes un bloque `import` con la dirección del recurso en tu código (`to`) y el identificador real (`id`):"),
 ("code", "hcl", "import.tf", """import {
  to = aws_s3_bucket.legado
  id = "legado-123456789012"
}

import {
  to = aws_security_group.legado
  id = "sg-0abc123def4567890"
}"""),
 ("p", "¿Qué formato tiene el `id`? Depende de cada recurso. Está en la sección **Import** al final de su página en la documentación del provider. Por ejemplo, un bucket se importa por nombre, un security group por su ID `sg-…` y una ruta de tabla por `rtb-xxx_10.0.0.0/16`."),

 ("h", "Generar el código automáticamente"),
 ("p", "Escribir a mano el bloque `resource` que coincida exactamente con lo que existe es tedioso. Terraform puede **generarlo** por ti:"),
 ("term", """$ terraform plan -generate-config-out=generado.tf

aws_s3_bucket.legado: Preparing import... [id=legado-123456789012]
aws_security_group.legado: Preparing import... [id=sg-0abc123def4567890]
aws_s3_bucket.legado: Refreshing state...
aws_security_group.legado: Refreshing state...

Terraform will perform the following actions:

  # aws_s3_bucket.legado will be imported
  # (config will be generated)
    resource "aws_s3_bucket" "legado" { ... }

  # aws_security_group.legado will be imported
  # (config will be generated)
    resource "aws_security_group" "legado" { ... }

Plan: 2 to import, 0 to add, 0 to change, 0 to destroy.

Terraform has generated configuration and written it to generado.tf."""),
 ("code", "hcl", "generado.tf (fragmento)", """# __generated__ by Terraform
resource "aws_security_group" "legado" {
  description            = "Creado a mano"
  egress                 = [{ cidr_blocks = ["0.0.0.0/0"], description = "", from_port = 0, ... }]
  ingress                = []
  name                   = "legado-sg"
  name_prefix            = null
  revoke_rules_on_delete = null
  tags                   = {}
  tags_all               = {}
  vpc_id                 = "vpc-0123456789abcdef0"
}"""),
 ("p", "El código generado funciona pero es «feo». **Límpialo** antes de aplicar:"),
 ("ul", [
  "Quita los argumentos con `null` o vacíos que no necesitas.",
  "Quita atributos solo de lectura o calculados (`tags_all`, `arn`…) si aparecen.",
  "Sustituye valores fijos por referencias (`vpc_id = data.aws_vpc.default.id`).",
  "Muévelo al archivo que le corresponda (`main.tf`, `network.tf`…).",
 ]),
 ("p", "Repite `terraform plan` hasta que diga **solo** importaciones, sin cambios:"),
 ("term", """Plan: 2 to import, 0 to add, 0 to change, 0 to destroy."""),
 ("p", "Entonces aplica. A partir de ese momento los recursos están gestionados por Terraform. Los bloques `import` se pueden borrar después (o dejarlos como documentación; ya no hacen nada)."),
 ("warn", "Si el plan muestra cambios (`~`) en un recurso importado, significa que tu código no coincide con la realidad y al aplicar **modificarías el recurso**. Ajusta el código hasta que no haya diferencias, salvo que el cambio sea intencionado."),

 ("h", "El comando clásico terraform import"),
 ("p", "Antes de los bloques `import` se usaba un comando. Sigue funcionando y lo verás en documentación antigua:"),
 ("code", "bash", "terminal", """# 1. escribe primero el bloque resource vacío o completo en el código
# 2. importa:
terraform import aws_s3_bucket.legado legado-123456789012"""),
 ("table", ["", "Bloque `import`", "Comando `terraform import`"], [
  ["Se ve en el plan antes de aplicar", "Sí", "No: modifica el estado directamente"],
  ["Genera código", "Sí (`-generate-config-out`)", "No"],
  ["Varios recursos a la vez", "Sí", "Uno por comando"],
  ["Revisable en un Pull Request", "Sí", "No"],
  ["Con `for_each`", "Sí (1.7+)", "No"],
 ]),

 ("h", "Refactorizar con moved"),
 ("p", "Refactorizar es reorganizar el código sin cambiar lo que hace. En Terraform el peligro es que **cambiar la dirección** de un recurso (renombrarlo o meterlo en un módulo) hace que Terraform lo destruya y lo cree de nuevo. El bloque `moved` lo evita:"),
 ("code", "hcl", "renombrar un recurso", """# Antes: resource "aws_instance" "servidor" { ... }
# Ahora:
resource "aws_instance" "web" {
  # ... mismo contenido ...
}

moved {
  from = aws_instance.servidor
  to   = aws_instance.web
}"""),
 ("term", """  # aws_instance.servidor has moved to aws_instance.web
    resource "aws_instance" "web" {
        id = "i-0123456789abcdef0"
        # (no changes)
    }

Plan: 0 to add, 0 to change, 0 to destroy."""),
 ("p", "También funciona para **meter recursos en un módulo**, algo muy común cuando el código crece:"),
 ("code", "hcl", "mover a un módulo", """# Antes los recursos estaban en el root: aws_s3_bucket.web, aws_s3_object.index
# Ahora están en module "web" (source = "./modules/static-site")

moved {
  from = aws_s3_bucket.web
  to   = module.web.aws_s3_bucket.this
}

moved {
  from = aws_s3_object.index
  to   = module.web.aws_s3_object.index
}"""),
 ("p", "Y para pasar de `count` a `for_each`:"),
 ("code", "hcl", "count → for_each", """moved {
  from = aws_iam_user.equipo[0]
  to   = aws_iam_user.equipo["ana"]
}"""),
 ("tip", "Ventaja de `moved` frente a `terraform state mv`: queda en el código, se revisa en el PR y funciona automáticamente en todos los entornos y para todo el equipo. Déjalos en el código un tiempo (o para siempre en módulos públicos) para que todos los usuarios migren."),

 ("h", "Soltar recursos con removed (1.7+)"),
 ("p", "¿Y si quieres que Terraform deje de gestionar un recurso **sin destruirlo**? Por ejemplo, porque pasa a otro equipo o a otro repositorio. Borra el bloque `resource` y añade:"),
 ("code", "hcl", "removed", """removed {
  from = aws_s3_bucket.antiguo

  lifecycle {
    destroy = false   # olvidarlo, no destruirlo
  }
}"""),
 ("term", """  # aws_s3_bucket.antiguo will no longer be managed by Terraform
    resource "aws_s3_bucket" "antiguo" {
        id = "antiguo-123456789012"
    }

Plan: 0 to add, 0 to change, 0 to destroy."""),
 ("p", "Es la versión declarativa de `terraform state rm`."),

 ("h", "Estrategia para migrar una cuenta entera"),
 ("ol", [
  "Haz inventario: lista los recursos (AWS Resource Explorer, `aws resourcegroupstaggingapi get-resources`, la factura).",
  "Agrupa por dominios (red, datos, aplicaciones) y empieza por lo que menos cambia (la red).",
  "Escribe bloques `import` y genera el código con `-generate-config-out`.",
  "Limpia, introduce variables y módulos, y repite `plan` hasta *0 to change*.",
  "Aplica y protege los recursos críticos con `prevent_destroy`.",
  "A partir de ahí, **prohíbe los cambios manuales** (permisos de solo lectura en la consola) para evitar drift.",
 ]),
 ("info", "Existen herramientas como **Terraformer** o **former2** que generan código de cuentas enteras. Útiles como punto de partida, pero el código resultante requiere mucha limpieza; el bloque `import` nativo suele ser mejor opción hoy."),
]

TEST = [
 ("¿Qué hace importar un recurso?",
  ["Lo copia a otra cuenta", "Asocia un recurso existente con un bloque de tu código, añadiéndolo al estado", "Lo recrea con Terraform", "Descarga su código del Registry"], 1,
  "El recurso no se modifica; Terraform empieza a gestionarlo."),
 ("¿Dónde encuentras el formato del `id` para importar un recurso?",
  ["En el estado", "En la sección Import de la documentación del recurso", "En la consola de AWS siempre es el ARN", "Es siempre el nombre"], 1,
  "Cada tipo de recurso usa un identificador distinto."),
 ("¿Qué comando genera código HCL para los bloques `import` que aún no tienen resource?",
  ["terraform import -generate", "terraform plan -generate-config-out=archivo.tf", "terraform show -hcl", "terraform fmt -generate"], 1,
  "Genera los bloques resource a partir de lo que existe."),
 ("Tras importar, el plan muestra `~ tags = { ... }`. ¿Qué significa?",
  ["Que la importación falló", "Que tu código no coincide con la realidad y aplicar modificaría el recurso", "Que todo está bien", "Que hay que reiniciar"], 1,
  "Ajusta el código hasta que el plan no tenga cambios (salvo los intencionados)."),
 ("Renombras `aws_instance.a` a `aws_instance.b`. ¿Qué bloque evita recrear la instancia?",
  ["import", "removed", "moved", "lifecycle"], 2, "`moved { from = aws_instance.a  to = aws_instance.b }`."),
 ("¿Qué hace `removed { from = X  lifecycle { destroy = false } }`?",
  ["Destruye X", "Deja de gestionar X sin destruirlo", "Mueve X a otro módulo", "Importa X"], 1,
  "Equivale de forma declarativa a `terraform state rm`."),
]

RETOS = [
 {"titulo": "Rescate completo",
  "enunciado": "Crea a mano (con la CLI o la consola) un bucket con una etiqueta `Origen = manual`. Impórtalo con un bloque `import` y `-generate-config-out`, limpia el código, cambia la etiqueta a `Origen = terraform` desde el código y aplica.",
  "pista": "Primero consigue un plan con `1 to import, 0 to change`; después haz el cambio de etiqueta en un segundo paso.",
  "solucion": ("hcl", """import {
  to = aws_s3_bucket.rescatado
  id = "NOMBRE-DEL-BUCKET"
}

# Tras generar y limpiar:
resource "aws_s3_bucket" "rescatado" {
  bucket = "NOMBRE-DEL-BUCKET"
  tags = {
    Origen = "terraform"   # paso 2: cambiado desde el código
  }
}

# terraform plan -generate-config-out=generado.tf
# limpiar → terraform apply   (1 imported)
# cambiar etiqueta → terraform apply   (1 changed)""")},
 {"titulo": "Refactor a módulo sin downtime",
  "enunciado": "Tienes en el root `random_pet.nombre` y `local_file.saludo` (del módulo 2). Muévelos a un módulo `modules/saludo` sin que se recreen.",
  "pista": "Necesitas un bloque `moved` por recurso, con `to = module.saludo.TIPO.NOMBRE`.",
  "solucion": ("hcl", """# modules/saludo/main.tf contiene ahora random_pet.nombre y local_file.saludo
# (usa path.root en filename si quieres conservar la misma ruta)

module "saludo" {
  source = "./modules/saludo"
}

moved {
  from = random_pet.nombre
  to   = module.saludo.random_pet.nombre
}

moved {
  from = local_file.saludo
  to   = module.saludo.local_file.saludo
}
# terraform init && terraform plan → 0 to add, 0 to change, 0 to destroy""")},
]
