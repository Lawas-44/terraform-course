# -*- coding: utf-8 -*-
# Módulo 12 · Importar y refactorizar

LECCION = [
 ("h", "Recursos creados a mano"),
 ("p", "Es muy habitual encontrarse recursos que alguien creó a mano en la web de AWS. No hace falta borrarlos y crearlos de nuevo con Terraform: se pueden **importar**. Importar significa decirle a Terraform: «este recurso que ya existe corresponde a este bloque de mi código»."),
 ("p", "Para practicar, crea un bucket a mano desde la terminal:"),
 ("term", """$ aws s3api create-bucket --bucket legado-123456789012 --region eu-west-1 \\
    --create-bucket-configuration LocationConstraint=eu-west-1"""),

 ("h", "El bloque import"),
 ("p", "Escribe un bloque `import` con dos datos: dónde va en tu código (`to`) y cuál es el recurso real (`id`):"),
 ("code", "hcl", "import.tf", """import {
  to = aws_s3_bucket.legado
  id = "legado-123456789012"
}"""),
 ("p", "¿Qué hay que poner en `id`? Depende del recurso. Lo dice la documentación de cada recurso, al final, en el apartado *Import*. Para un bucket es su nombre."),

 ("h", "Generar el código automáticamente"),
 ("p", "Terraform puede escribir por ti el bloque `resource` mirando cómo es el recurso real:"),
 ("term", """$ terraform plan -generate-config-out=generado.tf

aws_s3_bucket.legado: Preparing import... [id=legado-123456789012]

  # aws_s3_bucket.legado will be imported
  # (config will be generated)

Plan: 1 to import, 0 to add, 0 to change, 0 to destroy.

Terraform has generated configuration and written it to generado.tf."""),
 ("p", "Abre `generado.tf`. El código funciona, pero tiene muchas líneas que no hacen falta. **Límpialo**: deja solo lo importante."),
 ("code", "hcl", "generado.tf (limpio)", """resource "aws_s3_bucket" "legado" {
  bucket = "legado-123456789012"
}"""),
 ("p", "Ejecuta `terraform plan` hasta que diga que **solo hay que importar**, sin cambios:"),
 ("term", """$ terraform plan
Plan: 1 to import, 0 to add, 0 to change, 0 to destroy.
$ terraform apply"""),
 ("warn", "Si el plan muestra cambios (`~`) en el recurso importado, tu código no coincide con la realidad y al aplicar **modificarías el recurso**. Ajusta el código hasta que no haya cambios."),
 ("info", "Antes existía solo el comando `terraform import`. Sigue funcionando, pero el bloque `import` es mejor porque ves el plan antes y puede generar el código."),

 ("h", "Cambiar nombres sin borrar nada: moved"),
 ("p", "Si cambias el nombre de un recurso en el código, Terraform cree que es uno nuevo: borra el viejo y crea otro. Con un bloque `moved` le explicas que es el mismo:"),
 ("code", "hcl", "moved.tf", """resource "aws_instance" "web" {
  # ... antes se llamaba "servidor" ...
}

moved {
  from = aws_instance.servidor
  to   = aws_instance.web
}"""),
 ("term", """$ terraform plan
  # aws_instance.servidor has moved to aws_instance.web

Plan: 0 to add, 0 to change, 0 to destroy."""),
 ("p", "También sirve para mover recursos dentro de un módulo:"),
 ("code", "hcl", "mover a un módulo", """moved {
  from = aws_s3_bucket.web
  to   = module.web.aws_s3_bucket.this
}"""),
 ("tip", "`moved` hace lo mismo que `terraform state mv` (módulo 9), pero queda escrito en el código y funciona para todo el equipo."),

 ("h", "Dejar de gestionar sin borrar: removed"),
 ("p", "Si quieres que Terraform deje de gestionar un recurso pero **sin borrarlo**, quita su bloque `resource` y añade:"),
 ("code", "hcl", "removed.tf", """removed {
  from = aws_s3_bucket.antiguo

  lifecycle {
    destroy = false
  }
}"""),
 ("p", "El recurso sigue existiendo en AWS; Terraform simplemente se olvida de él."),
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
