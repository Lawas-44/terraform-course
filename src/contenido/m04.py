# -*- coding: utf-8 -*-
# Módulo 04 · Variables, outputs y locals

LECCION = [
 ("h", "Para qué sirven"),
 ("p", "Hasta ahora escribíamos los valores directamente en el código. Pero a menudo quieres usar el mismo código con datos distintos: un entorno de pruebas pequeño y uno de producción grande, un nombre u otro..."),
 ("table", ["Herramienta", "Qué es", "Cómo se usa"], [
  ["**variable**", "Un dato de entrada que puedes cambiar", "`var.nombre`"],
  ["**output**", "Un dato que se muestra al terminar", "bloque `output`"],
  ["**locals**", "Un valor de ayuda calculado dentro del código", "`local.nombre`"],
 ]),

 ("h", "Crear una variable"),
 ("p", "Una variable se crea con un bloque `variable`. Lo recomendable es indicar su tipo y una descripción:"),
 ("code", "hcl", "variables.tf", """variable "proyecto" {
  description = "Nombre del proyecto"
  type        = string
}

variable "entorno" {
  description = "Entorno: dev o prod"
  type        = string
  default     = "dev"
}

variable "replicas" {
  type    = number
  default = 1
}"""),
 ("ul", [
  "`type`: el tipo de dato (`string` es texto, `number` es número, `bool` es verdadero/falso).",
  "`default`: el valor si nadie da otro. Si una variable **no tiene default, es obligatoria**.",
 ]),
 ("p", "Para usarla escribe `var.` delante del nombre:"),
 ("code", "hcl", "main.tf", """resource "local_file" "config" {
  filename = "${var.proyecto}-${var.entorno}.conf"
  content  = "replicas=${var.replicas}"
}"""),
 ("p", "Si una variable obligatoria no tiene valor, Terraform te lo pregunta:"),
 ("term", """$ terraform plan
var.proyecto
  Nombre del proyecto

  Enter a value: tienda"""),

 ("h", "Comprobar que el valor es correcto"),
 ("p", "Con un bloque `validation` puedes rechazar valores incorrectos antes de crear nada:"),
 ("code", "hcl", "variables.tf", """variable "entorno" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "prod"], var.entorno)
    error_message = "El entorno debe ser dev o prod."
  }
}"""),
 ("term", """$ terraform plan -var="entorno=pruebas"
Error: Invalid value for variable

El entorno debe ser dev o prod."""),

 ("h", "Dar valores a las variables"),
 ("p", "Hay varias formas. La más cómoda es un archivo `terraform.tfvars`, que Terraform lee solo:"),
 ("code", "hcl", "terraform.tfvars", """proyecto = "tienda"
entorno  = "dev\""""),
 ("p", "Otras formas:"),
 ("term", """$ terraform plan -var="entorno=prod"
$ terraform plan -var-file="prod.tfvars"
$ export TF_VAR_proyecto=tienda"""),
 ("p", "Si el mismo valor está en varios sitios, gana el de más abajo en esta tabla:"),
 ("table", ["Prioridad", "Dónde está el valor"], [
  ["1 (la más baja)", "`default` de la variable"],
  ["2", "Variable de entorno `TF_VAR_nombre`"],
  ["3", "Archivo `terraform.tfvars`"],
  ["4", "Archivos `*.auto.tfvars`"],
  ["5 (la más alta)", "`-var` o `-var-file` al ejecutar el comando"],
 ]),
 ("tip", "Una forma ordenada de trabajar: lo común en `terraform.tfvars` y un archivo por entorno (`dev.tfvars`, `prod.tfvars`) que pasas con `-var-file`."),

 ("h", "Outputs: mostrar resultados"),
 ("p", "Los outputs muestran datos útiles al terminar, como una dirección web o un nombre:"),
 ("code", "hcl", "outputs.tf", """output "archivo" {
  description = "Archivo generado"
  value       = local_file.config.filename
}"""),
 ("term", """$ terraform output
archivo = "tienda-dev.conf"
$ terraform output -raw archivo
tienda-dev.conf"""),
 ("p", "Con `-raw` sale el valor sin comillas, útil para usarlo en otros comandos."),

 ("h", "Locals: no repetir"),
 ("p", "Si escribes lo mismo muchas veces, guárdalo en un `local`. A diferencia de una variable, un local **no se puede cambiar desde fuera**: es un cálculo interno."),
 ("code", "hcl", "locals.tf", """locals {
  prefijo = "${var.proyecto}-${var.entorno}"

  etiquetas = {
    Proyecto = var.proyecto
    Entorno  = var.entorno
  }
}

resource "local_file" "config" {
  filename = "${local.prefijo}.conf"
  content  = jsonencode(local.etiquetas)
}"""),

 ("h", "Valores secretos"),
 ("p", "Si una variable o un output contiene una contraseña, márcalo con `sensitive = true`. Así Terraform no la muestra en pantalla:"),
 ("code", "hcl", "secretos", """variable "db_password" {
  type      = string
  sensitive = true
}"""),
 ("term", """$ terraform apply
...
Outputs:
password = <sensitive>"""),
 ("warn", "`sensitive` solo **oculta** el valor en pantalla. El valor sigue guardado sin cifrar en el archivo de estado (`terraform.tfstate`). Por eso ese archivo nunca se comparte."),
]

TEST = [
 ("¿Cómo se lee el valor de la variable `region` dentro del código?",
  ["variable.region", "var.region", "${region}", "local.region"], 1, "Las variables se referencian con el prefijo `var.`."),
 ("Una variable sin `default`…",
  ["toma el valor null", "es obligatoria: hay que darle valor o Terraform lo pedirá", "provoca un error de sintaxis", "vale cadena vacía"], 1,
  "Sin default, Terraform necesita que le des un valor por alguna vía."),
 ("`entorno` vale \"dev\" en terraform.tfvars y ejecutas `terraform plan -var=\"entorno=prod\"`. ¿Qué valor usa?",
  ["dev", "prod", "Da error por conflicto", "El default"], 1, "Los flags de la línea de comandos tienen la máxima prioridad."),
 ("¿Qué variable de entorno da valor a `var.proyecto`?",
  ["PROYECTO", "TF_PROYECTO", "TF_VAR_proyecto", "VAR_proyecto"], 2, "El prefijo es `TF_VAR_` seguido del nombre exacto de la variable."),
 ("¿Qué hace realmente `sensitive = true`?",
  ["Cifra el valor en el estado", "Oculta el valor en la salida por pantalla", "Lo guarda en AWS Secrets Manager", "Impide usar la variable"], 1,
  "El valor sigue en texto plano en el estado."),
 ("¿Cuándo es mejor un `local` que una `variable`?",
  ["Cuando el usuario debe poder cambiarlo", "Cuando es un valor calculado interno que se repite", "Nunca", "Para secretos"], 1,
  "Los locals evitan repetición y no son configurables desde fuera."),
 ("¿Qué comando devuelve un output sin comillas, listo para un script?",
  ["terraform output -json", "terraform output -raw nombre", "terraform show", "terraform output --plain"], 1, "`-raw` imprime el valor tal cual."),
]

RETOS = [
 {"titulo": "Configuración multi-entorno",
  "enunciado": "Crea un proyecto con las variables `proyecto` (obligatoria, validada), `entorno` (validada) y `replicas`. Genera un archivo `<proyecto>-<entorno>.json` con un objeto que contenga las tres. Crea `dev.tfvars` y `prod.tfvars` y comprueba que generan archivos distintos.",
  "pista": "`jsonencode()` convierte un objeto HCL en texto JSON.",
  "solucion": ("hcl", """# variables.tf
variable "proyecto" {
  type = string
  validation {
    condition     = length(var.proyecto) >= 3
    error_message = "Mínimo 3 caracteres."
  }
}

variable "entorno" {
  type = string
  validation {
    condition     = contains(["dev", "prod"], var.entorno)
    error_message = "Solo dev o prod."
  }
}

variable "replicas" {
  type    = number
  default = 1
}

# main.tf
resource "local_file" "config" {
  filename = "${path.module}/${var.proyecto}-${var.entorno}.json"
  content = jsonencode({
    proyecto = var.proyecto
    entorno  = var.entorno
    replicas = var.replicas
  })
}

# dev.tfvars  →  proyecto = "tienda"  entorno = "dev"
# prod.tfvars →  proyecto = "tienda"  entorno = "prod"  replicas = 3
# terraform apply -var-file=dev.tfvars""")},
 {"titulo": "Adivina la precedencia",
  "enunciado": "`default = \"a\"`, `export TF_VAR_x=b`, `terraform.tfvars` con `x = \"c\"`, `z.auto.tfvars` con `x = \"d\"`. Ejecutas `terraform plan`. ¿Qué valor tiene `var.x`? ¿Y si añades `-var=x=e`?",
  "pista": "Repasa la tabla de prioridades.",
  "solucion": ("text", """Sin -var  → "d"  (*.auto.tfvars gana a terraform.tfvars, entorno y default)
Con -var  → "e"  (la línea de comandos gana a todo)""")},
]
