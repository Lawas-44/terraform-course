# -*- coding: utf-8 -*-
# Módulo 00 · Introducción a la Infraestructura como Código
# Formato de bloques: ver src/README.md

LECCION = [
 ("h", "El problema: infraestructura hecha a mano"),
 ("p", "Imagina que trabajas en una empresa que tiene una web. Para que funcione hace falta una red, un par de servidores, una base de datos, un balanceador de carga, reglas de firewall, un dominio y certificados. Alguien entró un día en la consola web del proveedor cloud y lo creó todo **haciendo clic**. A esto se le llama, medio en broma, *ClickOps*."),
 ("p", "Funciona… hasta que aparecen las preguntas incómodas:"),
 ("ul", [
  "**¿Cómo lo repito?** Hay que montar un entorno de pruebas idéntico al de producción. ¿Alguien recuerda los 140 clics exactos?",
  "**¿Quién cambió esto?** El firewall tiene un puerto abierto que nadie recuerda haber abierto.",
  "**¿Qué pasa si se borra?** Si alguien elimina el servidor por error, ¿cuánto tardamos en reconstruirlo igual?",
  "**¿Cuánto tenemos?** Nadie sabe con certeza qué recursos existen ni cuánto cuestan.",
 ]),
 ("p", "La **Infraestructura como Código** (IaC, *Infrastructure as Code*) responde a todas: en lugar de hacer clics, **describes la infraestructura en archivos de texto**. Esos archivos se guardan en Git, se revisan, se comentan y se pueden ejecutar tantas veces como quieras para obtener siempre el mismo resultado."),
 ("table", ["Infraestructura manual", "Infraestructura como Código"], [
  ["Pasos en la memoria de alguien", "Todo escrito en archivos versionados"],
  ["Difícil de repetir", "Repetible en segundos: dev, staging, prod…"],
  ["Sin historial de cambios", "Historial completo en Git (quién, qué, cuándo, por qué)"],
  ["Los errores se descubren en producción", "Los cambios se revisan antes de aplicarse (plan + Pull Request)"],
  ["Recuperarse de un desastre lleva días", "Se vuelve a aplicar el código"],
 ]),

 ("h", "Declarativo vs imperativo"),
 ("p", "Hay dos formas de dar instrucciones a una máquina. Piensa en pedir un café:"),
 ("ul", [
  "**Imperativo** (los pasos): «Muele 18 g de café, calienta agua a 92 °C, vierte 36 ml durante 25 segundos, sírvelo en taza pequeña».",
  "**Declarativo** (el resultado): «Quiero un espresso».",
 ]),
 ("p", "Terraform es **declarativo**: tú describes *qué* debe existir y Terraform calcula *cómo* conseguirlo. Si ya existe, no hace nada; si falta algo, lo crea; si sobra, lo elimina; si es distinto, lo modifica."),
 ("code", "bash", "Imperativo (script con la CLI de AWS)", """# Si lo ejecutas dos veces, crea DOS buckets... o falla.
aws s3api create-bucket --bucket mi-web-fotos --region eu-west-1 \\
  --create-bucket-configuration LocationConstraint=eu-west-1
aws s3api put-bucket-versioning --bucket mi-web-fotos \\
  --versioning-configuration Status=Enabled"""),
 ("code", "hcl", "Declarativo (Terraform)", """# Describe el resultado. Ejecutarlo 1 o 100 veces da lo mismo.
resource "aws_s3_bucket" "fotos" {
  bucket = "mi-web-fotos"
}

resource "aws_s3_bucket_versioning" "fotos" {
  bucket = aws_s3_bucket.fotos.id

  versioning_configuration {
    status = "Enabled"
  }
}"""),
 ("p", "Esa propiedad de «aplicarlo varias veces da el mismo resultado» se llama **idempotencia**, y es la clave de por qué la IaC es tan segura de usar."),
 ("tip", "No te preocupes si aún no entiendes la sintaxis del ejemplo. En el módulo 3 la veremos línea a línea."),

 ("h", "¿Dónde encaja Terraform? Tipos de herramientas"),
 ("p", "En el mundo IaC hay dos grandes familias de herramientas, y a menudo se usan juntas:"),
 ("table", ["Familia", "Para qué sirve", "Ejemplos"], [
  ["Aprovisionamiento", "Crear la infraestructura: redes, servidores, bases de datos, DNS…", "Terraform, OpenTofu, CloudFormation, Pulumi, Bicep"],
  ["Gestión de configuración", "Configurar lo que hay *dentro* de los servidores: paquetes, usuarios, archivos", "Ansible, Chef, Puppet, Salt"],
 ]),
 ("p", "Comparación rápida de las herramientas de aprovisionamiento más conocidas:"),
 ("table", ["Herramienta", "Lenguaje", "Nubes", "Comentario"], [
  ["Terraform", "HCL", "Todas (miles de providers)", "El estándar de facto; enorme comunidad"],
  ["OpenTofu", "HCL", "Todas", "Fork libre de Terraform; casi 100 % compatible"],
  ["AWS CloudFormation", "YAML/JSON", "Solo AWS", "Integrado en AWS, sin estado que gestionar"],
  ["Azure Bicep", "Bicep", "Solo Azure", "Equivalente de CloudFormation en Azure"],
  ["Pulumi", "TypeScript, Python, Go…", "Todas", "Usa lenguajes de programación generales"],
 ]),
 ("p", "La gran ventaja de Terraform es que **un único lenguaje y un único flujo de trabajo** sirven para AWS, Azure, Google Cloud, Kubernetes, GitHub, Cloudflare, Datadog y cientos de servicios más."),

 ("h", "Terraform y OpenTofu"),
 ("p", "Terraform lo creó HashiCorp en 2014 con licencia de código abierto. En agosto de 2023 HashiCorp cambió la licencia a **BSL** (Business Source License), que limita a otras empresas usarlo para crear productos competidores. Como respuesta, la comunidad creó **OpenTofu**, un fork gestionado por la Linux Foundation."),
 ("ul", [
  "Para aprender y para usarlo en tu empresa, la licencia de Terraform **no te afecta**.",
  "OpenTofu usa los mismos archivos `.tf` y los mismos comandos cambiando `terraform` por `tofu`.",
  "Todo lo de este curso funciona en ambos (las pocas diferencias se indican cuando aparecen).",
 ]),

 ("h", "Cómo funciona Terraform por dentro"),
 ("p", "Terraform tiene tres piezas que conviene tener claras desde el principio:"),
 ("ol", [
  "**Terraform Core**: el programa `terraform` que instalas. Lee tus archivos, calcula qué hay que cambiar y coordina todo.",
  "**Providers**: plugins que saben hablar con una API concreta (AWS, Azure, Docker, GitHub…). Se descargan automáticamente del **Terraform Registry**.",
  "**Estado (state)**: un archivo JSON donde Terraform apunta qué recursos ha creado y con qué datos. Es su «memoria».",
 ]),
 ("code", "text", "Flujo simplificado", """   tus archivos .tf          estado (terraform.tfstate)
          │                           │
          └──────────┐   ┌────────────┘
                     ▼   ▼
               ┌──────────────┐
               │Terraform Core│  ── calcula el plan
               └──────┬───────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
     provider AWS  provider    provider
          │        GitHub      Docker
          ▼           ▼           ▼
        API AWS   API GitHub  Docker Engine"""),
 ("p", "Y el ciclo de trabajo que repetirás durante todo el curso:"),
 ("table", ["Paso", "Comando", "Qué hace"], [
  ["1. Escribir", "(tu editor)", "Describes la infraestructura en archivos `.tf`"],
  ["2. Inicializar", "`terraform init`", "Descarga los providers necesarios"],
  ["3. Planificar", "`terraform plan`", "Enseña qué va a cambiar, sin tocar nada"],
  ["4. Aplicar", "`terraform apply`", "Ejecuta los cambios"],
  ["5. Destruir", "`terraform destroy`", "Elimina todo lo creado (muy útil al aprender)"],
 ]),
 ("info", "Terraform **no** instala software dentro de los servidores ni sustituye a Ansible. Su trabajo es crear, modificar y eliminar recursos a través de APIs."),

 ("h", "Casos de uso reales"),
 ("ul", [
  "Crear entornos completos en la nube (redes, máquinas, bases de datos) para cada equipo o cliente.",
  "Gestionar clústeres de Kubernetes y lo que corre en ellos.",
  "Administrar repositorios, equipos y permisos de GitHub o GitLab.",
  "Configurar DNS, CDN y certificados (Cloudflare, Route 53).",
  "Definir alertas y dashboards de monitorización (Datadog, Grafana).",
  "Montar entornos efímeros para pruebas que se destruyen al acabar.",
 ]),
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
