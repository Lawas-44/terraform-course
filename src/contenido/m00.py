# -*- coding: utf-8 -*-
# Módulo 00 · Introducción a la Infraestructura como Código
# Formato de bloques: ver src/README.md

LECCION = [
 ("h", "El problema: hacerlo todo a mano"),
 ("p", "Una web necesita varias piezas: servidores, una red, una base de datos, reglas de firewall... Lo habitual al empezar es crearlas **a mano**, haciendo clic en la web del proveedor de nube (AWS, Azure, Google Cloud)."),
 ("p", "Hacerlo a mano trae problemas:"),
 ("ul", [
  "**Es difícil de repetir.** Si necesitas una copia exacta para hacer pruebas, tienes que recordar todos los clics.",
  "**No queda registro.** Nadie sabe quién cambió algo ni cuándo.",
  "**Es fácil equivocarse.** Un clic de más y algo deja de funcionar.",
 ]),

 ("h", "La solución: Infraestructura como Código"),
 ("p", "La **Infraestructura como Código** (IaC) consiste en describir tus servidores, redes y bases de datos en **archivos de texto**. Una herramienta lee esos archivos y crea todo por ti."),
 ("p", "Ventajas:"),
 ("ul", [
  "Puedes repetirlo las veces que quieras y siempre sale igual.",
  "Guardas los archivos en Git, así que tienes el historial de todos los cambios.",
  "Otra persona puede revisar los cambios antes de aplicarlos.",
 ]),
 ("p", "**Terraform** es la herramienta de IaC más usada."),

 ("h", "Describir el resultado, no los pasos"),
 ("p", "Terraform es **declarativo**: tú describes **qué quieres tener**, no los pasos para conseguirlo. Es como pedir en un restaurante: dices «quiero un café» y no explicas cómo se hace."),
 ("p", "Ejemplo: este código dice «quiero un bucket (una carpeta en la nube) llamado mi-web-fotos»:"),
 ("code", "hcl", "main.tf", """resource "aws_s3_bucket" "fotos" {
  bucket = "mi-web-fotos"
}"""),
 ("p", "Si el bucket no existe, Terraform lo crea. Si ya existe, no hace nada. Puedes ejecutarlo muchas veces y el resultado es el mismo. A esto se le llama **idempotencia**."),
 ("info", "No te preocupes si aún no entiendes el código. Lo veremos paso a paso en los próximos módulos."),

 ("h", "Terraform y otras herramientas"),
 ("p", "Hay otras herramientas parecidas. Esta es la diferencia principal:"),
 ("table", ["Herramienta", "Para qué sirve"], [
  ["Terraform", "Crear infraestructura en cualquier nube (AWS, Azure, Google Cloud...) con el mismo lenguaje"],
  ["OpenTofu", "Una copia libre de Terraform. Funciona casi igual"],
  ["CloudFormation", "Lo mismo que Terraform, pero solo para AWS"],
  ["Ansible", "Configurar lo que hay **dentro** de los servidores (instalar programas, crear usuarios)"],
 ]),
 ("p", "En resumen: Terraform **crea** las piezas; herramientas como Ansible **configuran** lo que hay dentro."),

 ("h", "Las tres piezas de Terraform"),
 ("ol", [
  "**Terraform**: el programa que instalas en tu ordenador.",
  "**Providers**: complementos que saben hablar con cada servicio (uno para AWS, otro para Azure, otro para GitHub...). Se descargan solos.",
  "**Estado**: un archivo donde Terraform apunta lo que ha creado. Es su memoria.",
 ]),

 ("h", "Los cinco pasos que repetirás siempre"),
 ("table", ["Paso", "Comando", "Qué hace"], [
  ["1. Escribir", "(tu editor)", "Describes lo que quieres en archivos `.tf`"],
  ["2. Preparar", "`terraform init`", "Descarga los providers"],
  ["3. Revisar", "`terraform plan`", "Muestra qué va a cambiar, sin tocar nada"],
  ["4. Aplicar", "`terraform apply`", "Hace los cambios"],
  ["5. Borrar", "`terraform destroy`", "Elimina todo lo creado"],
 ]),
 ("term", """$ terraform init
$ terraform plan
$ terraform apply
$ terraform destroy"""),
 ('h', 'Terraform y Ansible: un equipo'),
 ('p', 'En este curso aprenderás dos herramientas que se usan juntas:'),
 ('table', ['Herramienta', 'Qué hace', 'Ejemplo'], [['**Terraform**', 'Crea la infraestructura', 'Crea dos servidores, una red y un firewall en AWS'], ['**Ansible**', 'Configura lo que hay dentro de los servidores', 'Instala nginx y publica tu web en esos servidores']]),
 ('p', 'Piensa en una casa: Terraform construye las paredes, las puertas y la instalación eléctrica; Ansible pone los muebles y lo deja todo listo para vivir.'),
 ('h', 'El proyecto del curso'),
 ('p', 'No solo vas a aprender teoría: a lo largo del curso construirás **tu propia web funcionando en AWS**. Cada módulo añade una pieza en la sección **Proyecto guiado**. Al final, un solo comando creará los servidores y los dejará configurados.'),
]

TEST = [
 ("¿Qué describe un archivo de Terraform?",
  ["Los pasos exactos que debe seguir el ordenador", "El estado final que debe tener la infraestructura", "Un script de Bash que se ejecuta en el servidor", "La factura mensual de la nube"],
  1, "Terraform es declarativo: describes el resultado deseado y él calcula los pasos."),
 ("¿Qué significa que una herramienta sea idempotente?",
  ["Que es muy rápida", "Que solo funciona en una nube", "Que aplicarla varias veces produce el mismo resultado", "Que no necesita Internet"],
  2, "Si la infraestructura ya está como describe el código, volver a aplicarlo no cambia nada."),
 ("¿Qué pieza de Terraform sabe hablar con la API de AWS?",
  ["El estado", "El provider de AWS", "Terraform Core", "El archivo .gitignore"],
  1, "Los providers son plugins que traducen tus recursos a llamadas a la API de cada servicio."),
 ("¿Cuál de estas tareas es más propia de Ansible que de Terraform?",
  ["Crear una VPC en AWS", "Crear un bucket de S3", "Instalar y configurar Nginx dentro de un servidor existente", "Crear un repositorio en GitHub"],
  2, "Configurar el interior de los servidores es gestión de configuración; Terraform se centra en aprovisionar recursos."),
 ("¿Qué es OpenTofu?",
  ["Una nube alternativa a AWS", "Un fork open source de Terraform, casi totalmente compatible", "Un editor de código", "Un provider de Terraform"],
  1, "Nació en 2023 tras el cambio de licencia de Terraform; usa los mismos archivos y comandos con `tofu`."),
 ("¿Qué comando enseña los cambios SIN aplicarlos?",
  ["terraform init", "terraform apply", "terraform plan", "terraform destroy"],
  2, "`plan` es una simulación: compara lo que describes con lo que existe y muestra las diferencias."),
]

RETOS = [
 {"titulo": "De clics a declaración",
  "enunciado": "Escribe en un papel (o un archivo de texto) los pasos manuales para montar un blog: un servidor, una base de datos, un dominio. Después reescríbelo como una lista de «cosas que deben existir» con sus características (tamaño, nombre, región…).",
  "pista": "La versión declarativa no tiene verbos como «crear» o «ir a»; solo sustantivos y propiedades.",
  "solucion": ("text", """Imperativo:
1. Entrar en la consola, ir a EC2 → Launch instance
2. Elegir Ubuntu, t3.micro, abrir puertos 80 y 443
3. Ir a RDS → Create database → MySQL, db.t3.micro
4. Ir a Route 53 → crear registro A apuntando a la IP

Declarativo:
- servidor "blog":     ubuntu, t3.micro, puertos 80/443 abiertos
- base_de_datos "blog": mysql, db.t3.micro, 20 GB
- registro_dns "www":  tipo A → IP del servidor "blog\"""")},
]


PROYECTO = {'titulo': 'Lo que vas a construir',
 'bloques': [('p', 'Al terminar el curso tendrás una web personal funcionando en dos servidores de AWS:'),
             ('ul',
              ['**Terraform** creará una red propia, un firewall, una clave SSH y dos servidores Ubuntu.',
               '**Ansible** instalará nginx en los servidores y publicará tu web, una página de estado y una '
               'zona privada con contraseña.',
               'Un **script** lo hará todo con un comando, y otro lo borrará.',
               '**GitHub Actions** revisará cada cambio que subas.']),
             ('code',
              'text',
              'resultado final',
              '   Tú                          Visitantes\n'
              '    |                               |\n'
              '    | Terraform + Ansible           | http://\n'
              '    v                               v\n'
              ' +------------------- AWS ------------------+\n'
              ' |   +--------+            +--------+       |\n'
              ' |   |  web1  |            |  web2  |       |\n'
              ' |   | nginx  |            | nginx  |       |\n'
              ' |   +--------+            +--------+       |\n'
              ' +------------------------------------------+'),
             ('p',
              'Cada módulo tiene un paso. Hazlos en orden y, si te atascas, compara con el código terminado '
              'en la carpeta `proyecto/` del repositorio del curso.'),
             ('p', 'En este módulo no hay nada que escribir todavía. Empezamos en el siguiente.')]}
