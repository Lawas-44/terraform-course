# -*- coding: utf-8 -*-
# Módulo 08 · Expresiones y funciones

LECCION = [
 ("h", "Operaciones básicas"),
 ("p", "Puedes hacer cuentas y comparaciones. Pruébalo en `terraform console`:"),
 ("term", """$ terraform console
> 10 + 5
15
> 5 > 3
true
> "dev" == "prod"
false"""),

 ("h", "Elegir entre dos valores"),
 ("p", "Para elegir un valor según una condición se escribe `condición ? si_es_verdad : si_es_falso`:"),
 ("code", "hcl", "condicionales", """locals {
  es_prod        = var.entorno == "prod"
  tipo_instancia = local.es_prod ? "t3.medium" : "t3.micro"
  replicas       = local.es_prod ? 3 : 1
}"""),
 ("p", "Se lee así: «si es producción, usa t3.medium; si no, t3.micro»."),
 ("warn", "Los dos valores deben ser del mismo tipo. `local.es_prod ? 3 : \"uno\"` da error porque mezcla un número y un texto."),

 ("h", "Recorrer listas con for"),
 ("p", "Una expresión `for` crea una lista nueva a partir de otra. Entre `[ ]` devuelve una lista y entre `{ }` un mapa:"),
 ("code", "hcl", "for", """locals {
  nombres = ["ana", "luis", "marta"]

  # Todos en mayúsculas
  mayusculas = [for n in local.nombres : upper(n)]
  # ["ANA", "LUIS", "MARTA"]

  # Solo los de más de 3 letras
  largos = [for n in local.nombres : n if length(n) > 3]
  # ["luis", "marta"]

  # Un mapa nombre => número de letras
  letras = { for n in local.nombres : n => length(n) }
  # { ana = 3, luis = 4, marta = 5 }
}"""),

 ("h", "Sacar un dato de todas las copias"),
 ("p", "Si creaste varias copias con `count`, el símbolo `[*]` saca un dato de todas a la vez:"),
 ("code", "hcl", "splat", """output "ips" {
  value = aws_instance.web[*].public_ip
}"""),

 ("h", "Bloques repetidos: dynamic"),
 ("p", "Algunos recursos tienen bloques internos que se repiten, como las reglas de un firewall. `dynamic` los genera desde una lista:"),
 ("code", "hcl", "dynamic", """resource "aws_security_group" "web" {
  name_prefix = "web-"

  dynamic "ingress" {
    for_each = [80, 443]
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}"""),
 ("p", "Genera dos reglas: una para el puerto 80 y otra para el 443."),

 ("h", "Funciones útiles"),
 ("p", "Terraform trae muchas funciones ya hechas. No puedes crear las tuyas. Estas son las más usadas:"),
 ("table", ["Función", "Ejemplo", "Resultado"], [
  ["`upper` / `lower`", "`lower(\"WEB\")`", "`\"web\"`"],
  ["`length`", "`length([1, 2, 3])`", "`3`"],
  ["`join`", "`join(\",\", [\"a\", \"b\"])`", "`\"a,b\"`"],
  ["`replace`", "`replace(\"a_b\", \"_\", \"-\")`", "`\"a-b\"`"],
  ["`contains`", "`contains([\"a\", \"b\"], \"b\")`", "`true`"],
  ["`merge`", "`merge({a = 1}, {b = 2})`", "`{a = 1, b = 2}`"],
  ["`lookup`", "`lookup({a = 1}, \"b\", 0)`", "`0` (valor por defecto)"],
  ["`max`", "`max(3, 7, 2)`", "`7`"],
  ["`try`", "`try(local.x.campo, \"nada\")`", "el valor o `\"nada\"` si falla"],
  ["`cidrsubnet`", "`cidrsubnet(\"10.0.0.0/16\", 8, 2)`", "`\"10.0.2.0/24\"`"],
  ["`jsonencode`", "`jsonencode({a = 1})`", "texto JSON"],
  ["`file`", "`file(\"script.sh\")`", "el contenido del archivo"],
 ]),

 ("h", "Dividir una red en partes: cidrsubnet"),
 ("p", "Una red se escribe como `10.0.0.0/16`. `cidrsubnet` la divide en redes más pequeñas (subredes). Con `8` como segundo número obtienes subredes `/24`, y el tercer número indica cuál quieres:"),
 ("term", """$ terraform console
> cidrsubnet("10.0.0.0/16", 8, 0)
"10.0.0.0/24"
> cidrsubnet("10.0.0.0/16", 8, 1)
"10.0.1.0/24"
> cidrsubnet("10.0.0.0/16", 8, 5)
"10.0.5.0/24\""""),

 ("h", "Escribir JSON sin errores"),
 ("p", "Algunos servicios piden datos en formato JSON (por ejemplo, los permisos de AWS). En lugar de escribirlo a mano, usa `jsonencode`, que siempre genera JSON correcto:"),
 ("code", "hcl", "permisos con jsonencode", """resource "aws_iam_policy" "lectura" {
  name = "lectura-s3"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = ["arn:aws:s3:::mi-bucket/*"]
    }]
  })
}"""),

 ("h", "Plantillas: templatefile"),
 ("p", "Para textos largos (como un script de arranque) puedes usar un archivo aparte y rellenar huecos con `templatefile`:"),
 ("code", "bash", "bienvenida.sh.tftpl", """#!/bin/bash
echo "Bienvenido al entorno ${entorno}" > /tmp/bienvenida.txt"""),
 ("code", "hcl", "main.tf", """resource "local_file" "script" {
  filename = "script.sh"
  content  = templatefile("bienvenida.sh.tftpl", { entorno = "dev" })
}"""),
]

TEST = [
 ("¿Qué devuelve `[for n in [\"a\", \"bb\", \"ccc\"] : length(n)]`?",
  ["[\"a\", \"bb\", \"ccc\"]", "[1, 2, 3]", "3", "{a = 1, bb = 2, ccc = 3}"], 1, "Una lista con la longitud de cada string."),
 ("¿Qué devuelve `{ for n in [\"a\", \"bb\"] : n => upper(n) }`?",
  ["[\"A\", \"BB\"]", "{ a = \"A\", bb = \"BB\" }", "Error", "{ \"A\", \"BB\" }"], 1, "Con llaves y `=>` se construye un map."),
 ("¿Qué devuelve `cidrsubnet(\"10.0.0.0/16\", 8, 5)`?",
  ["10.0.5.0/24", "10.5.0.0/16", "10.0.0.5/24", "10.0.8.0/21"], 0, "/16 + 8 bits = /24; la subred número 5 es 10.0.5.0/24."),
 ("¿Por qué `var.x ? 1 : \"no\"` da error?",
  ["Falta un if", "Las dos ramas devuelven tipos distintos", "No se puede usar var en condicionales", "Faltan paréntesis"], 1,
  "Ambas ramas deben ser del mismo tipo (o convertibles)."),
 ("¿Para qué sirve un bloque `dynamic`?",
  ["Para crear varios recursos", "Para generar bloques anidados repetidos dentro de un recurso", "Para cargar archivos", "Para variables dinámicas"], 1,
  "Genera bloques como `ingress`, `setting`… a partir de una colección."),
 ("¿Cuál es la mejor forma de escribir una política IAM en Terraform?",
  ["Un heredoc con JSON escrito a mano", "jsonencode() con un objeto HCL", "Un archivo .txt", "Un comentario"], 1,
  "jsonencode garantiza JSON válido y permite usar referencias y expresiones."),
 ("¿Qué devuelve `try(local.mapa.no_existe, \"defecto\")`?",
  ["Error", "null", "\"defecto\"", "\"no_existe\""], 2, "`try` devuelve la primera expresión que se evalúa sin error."),
]

RETOS = [
 {"titulo": "Plan de direcciones IP",
  "enunciado": "Dada la VPC `10.20.0.0/16` y las zonas `a`, `b`, `c`, genera en `locals` un map con, para cada zona, un objeto `{ publica = ..., privada = ... }`. Las públicas deben ser 10.20.0-2.0/24 y las privadas 10.20.100-102.0/24. Compruébalo en `terraform console`.",
  "pista": "`cidrsubnet(cidr, 8, i)` y `cidrsubnet(cidr, 8, i + 100)` dentro de un `for` con índice.",
  "solucion": ("hcl", """locals {
  cidr  = "10.20.0.0/16"
  zonas = ["a", "b", "c"]

  red = {
    for i, z in local.zonas : z => {
      publica = cidrsubnet(local.cidr, 8, i)
      privada = cidrsubnet(local.cidr, 8, i + 100)
    }
  }
}
# > local.red.b
# { privada = "10.20.101.0/24", publica = "10.20.1.0/24" }""")},
 {"titulo": "Etiquetas normalizadas",
  "enunciado": "Recibes `var.etiquetas = { \"Centro Coste\" = \"1234\", \"OWNER\" = \"Ana\" }`. Genera un map con las claves en minúsculas y con guiones en vez de espacios, y añade siempre `gestion = \"terraform\"`.",
  "pista": "`replace(lower(k), \" \", \"-\")` dentro de un `for`, y `merge` al final.",
  "solucion": ("hcl", """variable "etiquetas" {
  type = map(string)
  default = {
    "Centro Coste" = "1234"
    "OWNER"        = "Ana"
  }
}

locals {
  etiquetas_normalizadas = merge(
    { for k, v in var.etiquetas : replace(lower(k), " ", "-") => v },
    { gestion = "terraform" }
  )
}
# { "centro-coste" = "1234", gestion = "terraform", owner = "Ana" }""")},
]


PROYECTO = {'titulo': 'Genera el inventario de Ansible',
 'bloques': [('p',
              'Ansible necesitará la lista de servidores con sus IPs. En lugar de escribirla a mano, haz que '
              'Terraform la genere con una plantilla.'),
             ('code',
              'text',
              'terraform/templates/inventario.ini.tftpl',
              '# Archivo generado por Terraform. No lo edites a mano.\n'
              '[web]\n'
              '%{ for nombre, ip in servidores ~}\n'
              '${nombre} ansible_host=${ip}\n'
              '%{ endfor ~}\n'
              '\n'
              '[web:vars]\n'
              'ansible_user=ubuntu'),
             ('p', '`%{ for }` repite la línea por cada servidor. Añade a `main.tf`:'),
             ('code',
              'hcl',
              'terraform/main.tf (añadir)',
              'resource "local_file" "inventario" {\n'
              '  filename        = "${path.module}/../ansible/inventario/hosts.ini"\n'
              '  file_permission = "0644"\n'
              '  content = templatefile("${path.module}/templates/inventario.ini.tftpl", {\n'
              '    servidores = { for nombre, servidor in aws_instance.web : nombre => servidor.public_ip }\n'
              '  })\n'
              '}'),
             ('p', 'Añade también dos outputs útiles con expresiones `for`:'),
             ('code',
              'hcl',
              'terraform/outputs.tf (añadir)',
              'output "urls" {\n'
              '  description = "Dirección web de cada servidor"\n'
              '  value       = { for nombre, servidor in aws_instance.web : nombre => '
              '"http://${servidor.public_ip}" }\n'
              '}\n'
              '\n'
              'output "ssh" {\n'
              '  description = "Comando para entrar en cada servidor"\n'
              '  value       = { for nombre, servidor in aws_instance.web : nombre => "ssh '
              'ubuntu@${servidor.public_ip}" }\n'
              '}'),
             ('term',
              '$ terraform apply\n'
              '...\n'
              'Plan: 1 to add, 0 to change, 0 to destroy.\n'
              '$ cat ../ansible/inventario/hosts.ini\n'
              '# Archivo generado por Terraform. No lo edites a mano.\n'
              '[web]\n'
              'web1 ansible_host=54.170.10.20\n'
              'web2 ansible_host=54.170.10.21\n'
              '\n'
              '[web:vars]\n'
              'ansible_user=ubuntu'),
             ('p',
              'Resultado de este paso: Terraform escribe solo el inventario que usará Ansible a partir del '
              'módulo 13.')]}
