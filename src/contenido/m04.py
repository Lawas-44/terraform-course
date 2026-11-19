# -*- coding: utf-8 -*-
# Módulo 04 · Variables, outputs y locals

LECCION = [
 ("h", "Por qué parametrizar"),
 ("p", "Hasta ahora todos los valores estaban escritos «a fuego» en el código. Pero en la vida real quieres reutilizar la misma configuración con datos distintos: un entorno `dev` pequeño y barato y un `prod` grande, una región u otra, un nombre de proyecto u otro. Para eso existen tres herramientas:"),
 ("table", ["Herramienta", "Analogía", "Sintaxis"], [
  ["**variable**", "Los parámetros de una función", "`var.nombre`"],
  ["**output**", "El valor de retorno", "`output \"x\" { value = ... }`"],
  ["**locals**", "Variables internas de la función", "`local.nombre`"],
 ]),

 ("h", "Declarar variables"),
 ("p", "Una variable se declara con un bloque `variable`. Todos sus argumentos son opcionales, pero conviene poner al menos `type` y `description`:"),
 ("code", "hcl", "variables.tf", """variable "proyecto" {
  description = "Nombre del proyecto; se usa como prefijo"
  type        = string
  # sin default → es OBLIGATORIA
}

variable "entorno" {
  description = "Entorno de despliegue"
  type        = string
  default     = "dev"
}

variable "replicas" {
  description = "Número de copias"
  type        = number
  default     = 1
}

variable "habilitar_logs" {
  type    = bool
  default = false
}"""),
 ("p", "Y se usan con `var.NOMBRE`:"),
 ("code", "hcl", "main.tf", """resource "local_file" "config" {
  filename = "${path.module}/${var.proyecto}-${var.entorno}.conf"
  content  = "replicas=${var.replicas}\\nlogs=${var.habilitar_logs}\\n"
}"""),
 ("p", "Si una variable obligatoria no tiene valor, Terraform lo pregunta al ejecutar:"),
 ("term", """$ terraform plan
var.proyecto
  Nombre del proyecto; se usa como prefijo

  Enter a value: tienda"""),

 ("h", "Tipos complejos y optional()"),
 ("p", "Las variables pueden tener tipos complejos. Con `object` y `optional()` puedes definir estructuras con valores por defecto por campo:"),
 ("code", "hcl", "variables.tf", """variable "zonas" {
  type    = list(string)
  default = ["eu-west-1a", "eu-west-1b"]
}

variable "etiquetas_extra" {
  type    = map(string)
  default = {}
}

variable "servidor" {
  type = object({
    nombre  = string
    tamano  = optional(string, "t3.micro")  # opcional con valor por defecto
    puertos = optional(list(number), [80])
  })
}"""),
 ("code", "hcl", "terraform.tfvars", """servidor = {
  nombre = "web"
  # tamano y puertos toman sus valores por defecto
}"""),

 ("h", "Validaciones"),
 ("p", "Puedes impedir valores incorrectos **antes** de que Terraform intente crear nada. Un bloque `validation` tiene una condición y un mensaje de error:"),
 ("code", "hcl", "variables.tf", """variable "entorno" {
  type    = string
  default = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.entorno)
    error_message = "entorno debe ser dev, staging o prod."
  }
}

variable "replicas" {
  type    = number
  default = 1

  validation {
    condition     = var.replicas >= 1 && var.replicas <= 5
    error_message = "replicas debe estar entre 1 y 5."
  }
}

variable "proyecto" {
  type = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,20}$", var.proyecto))
    error_message = "Solo minúsculas, números y guiones (3-21 caracteres)."
  }
}"""),
 ("term", """$ terraform plan -var="entorno=pruebas"
╷
│ Error: Invalid value for variable
│
│   on variables.tf line 1:
│    1: variable "entorno" {
│
│ entorno debe ser dev, staging o prod.
╵"""),

 ("h", "Cómo dar valores a las variables"),
 ("p", "Hay cinco formas. De **menor a mayor prioridad** (la última gana):"),
 ("table", ["Prioridad", "Origen", "Ejemplo"], [
  ["1 (menor)", "Valor `default` de la variable", "`default = \"dev\"`"],
  ["2", "Variables de entorno `TF_VAR_nombre`", "`export TF_VAR_entorno=staging`"],
  ["3", "Archivo `terraform.tfvars` (y `terraform.tfvars.json`)", "se carga automáticamente"],
  ["4", "Archivos `*.auto.tfvars` (en orden alfabético)", "`comun.auto.tfvars`"],
  ["5 (mayor)", "`-var` y `-var-file` en la línea de comandos (en el orden escrito)", "`-var-file=prod.tfvars`"],
 ]),
 ("code", "hcl", "terraform.tfvars", """proyecto = "tienda"
entorno  = "dev"
replicas = 1"""),
 ("code", "hcl", "prod.tfvars", """entorno        = "prod"
replicas       = 3
habilitar_logs = true"""),
 ("code", "bash", "terminal", """terraform plan                         # usa terraform.tfvars
terraform plan -var-file="prod.tfvars" # prod.tfvars pisa a terraform.tfvars
terraform plan -var="replicas=2"       # un valor suelto

export TF_VAR_proyecto=tienda          # Bash
$env:TF_VAR_proyecto = "tienda"        # PowerShell"""),
 ("tip", "Patrón habitual: valores comunes en `terraform.tfvars` y un archivo por entorno (`dev.tfvars`, `prod.tfvars`) que se pasa con `-var-file`."),

 ("h", "Outputs"),
 ("p", "Los outputs muestran información útil al terminar (`apply`) y permiten que otros módulos o scripts la consuman:"),
 ("code", "hcl", "outputs.tf", """output "archivo_config" {
  description = "Ruta del archivo de configuración generado"
  value       = local_file.config.filename
}

output "resumen" {
  value = {
    proyecto = var.proyecto
    entorno  = var.entorno
    replicas = var.replicas
  }
}"""),
 ("term", """$ terraform output
archivo_config = "./tienda-dev.conf"
resumen = {
  "entorno" = "dev"
  "proyecto" = "tienda"
  "replicas" = 1
}

$ terraform output -raw archivo_config     # sin comillas: ideal para scripts
./tienda-dev.conf

$ terraform output -json resumen | jq -r .entorno
dev"""),

 ("h", "Locals: no te repitas"),
 ("p", "Cuando una misma expresión aparece varias veces, extráela a un `local`. Son valores internos, calculados, que **no** se pueden cambiar desde fuera:"),
 ("code", "hcl", "locals.tf", """locals {
  prefijo = "${var.proyecto}-${var.entorno}"

  etiquetas = merge(
    {
      Proyecto = var.proyecto
      Entorno  = var.entorno
      Gestion  = "terraform"
    },
    var.etiquetas_extra
  )

  es_prod = var.entorno == "prod"
}

resource "local_file" "config" {
  filename = "${path.module}/${local.prefijo}.conf"
  content  = jsonencode(local.etiquetas)
}"""),
 ("table", ["Usa una variable si…", "Usa un local si…"], [
  ["el valor lo decide quien usa el código", "el valor se calcula a partir de otros"],
  ["cambia entre entornos", "es igual siempre pero se repite"],
  ["debe documentarse como parámetro", "es un detalle interno"],
 ]),

 ("h", "Valores sensibles"),
 ("p", "Marca como `sensitive` las variables y outputs con secretos para que Terraform no los muestre por pantalla:"),
 ("code", "hcl", "secretos", """variable "db_password" {
  type      = string
  sensitive = true
}

output "cadena_conexion" {
  value     = "postgres://admin:${var.db_password}@db:5432/app"
  sensitive = true
}"""),
 ("term", """$ terraform apply
...
Outputs:
cadena_conexion = <sensitive>"""),
 ("warn", "`sensitive` **solo oculta** el valor en la salida. Sigue guardado en texto plano en `terraform.tfstate`. Para protegerlo de verdad hay que proteger el estado (módulo 10) y usar gestores de secretos (módulo 13). Y pasa los secretos por `TF_VAR_...`, nunca en un `.tfvars` subido a Git."),
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
