# -*- coding: utf-8 -*-
# Módulo 06 · Recursos, data sources y dependencias

LECCION = [
 ("h", "Argumentos y atributos"),
 ("p", "Cada recurso tiene dos tipos de datos:"),
 ("ul", [
  "**Argumentos**: lo que tú escribes (`instance_type = \"t3.micro\"`).",
  "**Atributos**: lo que el recurso expone después de crearse, incluidos los argumentos y valores calculados por la nube (`id`, `arn`, `public_ip`…).",
 ]),
 ("p", "Los atributos calculados aparecen en el plan como `(known after apply)` porque AWS los asigna en el momento de crear el recurso."),
 ("info", "Este módulo crea una instancia EC2 `t3.micro`, incluida en la capa gratuita de AWS en la mayoría de cuentas nuevas. Fuera de ella cuesta unos céntimos por hora. **Destruye todo al terminar.**"),

 ("h", "Data sources: leer lo que ya existe"),
 ("p", "Un bloque `data` **no crea nada**: consulta información que ya existe (en AWS o donde sea) para usarla en tu configuración. Se referencia con el prefijo `data.`:"),
 ("code", "hcl", "data.tf", """# ¿Quién soy? (cuenta y usuario actual)
data "aws_caller_identity" "actual" {}

# ¿En qué región estoy?
data "aws_region" "actual" {}

# Zonas de disponibilidad de la región
data "aws_availability_zones" "disponibles" {
  state = "available"
}

# La VPC por defecto que AWS crea en cada región
data "aws_vpc" "default" {
  default = true
}

# La imagen (AMI) más reciente de Amazon Linux 2023
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

output "info" {
  value = {
    cuenta = data.aws_caller_identity.actual.account_id
    region = data.aws_region.actual.region
    zonas  = data.aws_availability_zones.disponibles.names
    ami    = data.aws_ami.amazon_linux.id
  }
}"""),
 ("p", "¿Por qué no escribir el ID de la AMI directamente? Porque cambia en cada región y Amazon publica versiones nuevas cada pocas semanas. Con el data source siempre obtienes la correcta."),
 ("tip", "En el plan, los data sources aparecen con `<=` (*read*). Puedes probarlos con `terraform apply` sin crear ningún recurso."),

 ("h", "Dependencias implícitas y el grafo"),
 ("p", "Cuando un recurso hace referencia a otro, Terraform crea una **dependencia implícita**. Con todas ellas construye un **grafo** que decide el orden y qué puede hacerse en paralelo (por defecto, hasta 10 operaciones a la vez)."),
 ("code", "text", "grafo del ejemplo de este módulo", """data.aws_ami.amazon_linux ──────────────┐
                                        ▼
aws_security_group.web ──────────► aws_instance.web
        │
        ├──► aws_vpc_security_group_ingress_rule.http
        └──► aws_vpc_security_group_egress_rule.todo"""),
 ("p", "El security group y la AMI no dependen entre sí, así que se procesan **a la vez**. La instancia espera a ambos. Al destruir, el orden se invierte."),
 ("code", "bash", "ver el grafo", """# Necesita Graphviz: brew install graphviz / sudo apt install graphviz
terraform graph | dot -Tsvg > grafo.svg"""),

 ("h", "Dependencias explícitas: depends_on"),
 ("p", "A veces existe una dependencia que Terraform no puede ver porque no hay referencia directa. Por ejemplo, una aplicación que necesita que exista una política IAM aunque no la nombre. Para eso está `depends_on`:"),
 ("code", "hcl", "depends_on", """resource "aws_s3_bucket" "logs" {
  bucket_prefix = "logs-"
}

resource "aws_instance" "app" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"

  # la app escribe en el bucket al arrancar, pero no lo referenciamos
  depends_on = [aws_s3_bucket.logs]
}"""),
 ("warn", "Usa `depends_on` solo como último recurso. Si puedes pasar un valor de un recurso a otro, hazlo: la dependencia queda clara y Terraform optimiza mejor."),

 ("h", "Práctica: un servidor web en EC2"),
 ("p", "Vamos a desplegar un servidor web accesible desde Internet en la VPC por defecto. Necesitamos tres piezas: la imagen (AMI), un **security group** (el firewall) y la **instancia**."),
 ("code", "hcl", "versions.tf + providers.tf", """terraform {
  required_version = ">= 1.10"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = { Gestion = "terraform", Curso = "modulo-06" }
  }
}

variable "region" {
  type    = string
  default = "eu-west-1"
}"""),
 ("code", "hcl", "main.tf", """data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# Firewall: permite HTTP de entrada y todo de salida
resource "aws_security_group" "web" {
  name_prefix = "web-"
  description = "Permite HTTP desde Internet"
}

resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "todo" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1" # todos los protocolos
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  vpc_security_group_ids = [aws_security_group.web.id]

  # Script que se ejecuta en el primer arranque
  user_data = <<-EOF
    #!/bin/bash
    dnf install -y nginx
    echo "<h1>Hola desde Terraform</h1><p>Servidor: $(hostname)</p>" \\
      > /usr/share/nginx/html/index.html
    systemctl enable --now nginx
  EOF

  # Si cambia user_data, recrear la instancia para que se vuelva a ejecutar
  user_data_replace_on_change = true

  tags = {
    Name = "web-curso-terraform"
  }
}"""),
 ("code", "hcl", "outputs.tf", """output "ip_publica" {
  value = aws_instance.web.public_ip
}

output "url" {
  value = "http://${aws_instance.web.public_ip}"
}"""),
 ("term", """$ terraform apply
...
Plan: 4 to add, 0 to change, 0 to destroy.
...
aws_security_group.web: Creating...
aws_security_group.web: Creation complete after 2s [id=sg-0a1b2c3d4e5f]
aws_vpc_security_group_egress_rule.todo: Creating...
aws_vpc_security_group_ingress_rule.http: Creating...
aws_instance.web: Creating...
aws_instance.web: Still creating... [10s elapsed]
aws_instance.web: Creation complete after 13s [id=i-0123456789abcdef0]

Outputs:
ip_publica = "54.170.10.20"
url = "http://54.170.10.20"

$ curl $(terraform output -raw url)     # espera 1-2 minutos a que arranque nginx
<h1>Hola desde Terraform</h1><p>Servidor: ip-172-31-5-10...</p>"""),
 ("info", "Para entrar al servidor por terminal sin abrir el puerto 22, AWS ofrece *Session Manager* y *EC2 Instance Connect*. Lo veremos más adelante; de momento no abras SSH a todo Internet."),

 ("h", "¿Actualizar o reemplazar?"),
 ("p", "Haz pequeños cambios y observa el plan antes de aplicarlos:"),
 ("table", ["Cambio", "Resultado en el plan"], [
  ["Cambiar el tag `Name`", "`~` update in-place (instantáneo)"],
  ["Cambiar `instance_type` a `t3.small`", "`~` update in-place (AWS para y arranca la instancia)"],
  ["Cambiar `user_data`", "`-/+` reemplazo (por `user_data_replace_on_change`)"],
  ["Cambiar la `ami`", "`-/+` reemplazo: la máquina se destruye y se crea otra"],
  ["Cambiar la `description` del security group", "`-/+` reemplazo"],
 ]),
 ("warn", "Un reemplazo de un servidor significa una IP pública nueva y perder todo lo que hubiera en su disco. Por eso en infraestructura moderna los servidores se tratan como desechables (*cattle, not pets*) y los datos se guardan fuera (S3, bases de datos)."),

 ("h", "Leer el estado de un recurso"),
 ("code", "bash", "inspección", """terraform state list
# data.aws_ami.amazon_linux
# aws_instance.web
# aws_security_group.web
# ...

terraform state show aws_instance.web   # todos los atributos
terraform console
> aws_instance.web.availability_zone
"eu-west-1b"
> data.aws_ami.amazon_linux.name
"al2023-ami-2023.6.20261110.0-kernel-6.1-x86_64\""""),
 ("p", "Y al terminar, siempre:"),
 ("code", "bash", "terminal", "terraform destroy"),
]

TEST = [
 ("¿Qué diferencia hay entre `resource` y `data`?",
  ["Ninguna", "resource crea y gestiona; data solo lee información existente", "data crea recursos más baratos", "resource solo lee"], 1,
  "Los data sources consultan; nunca crean, modifican ni destruyen nada."),
 ("¿Cómo se referencia el ID de `data \"aws_ami\" \"linux\"`?",
  ["aws_ami.linux.id", "data.aws_ami.linux.id", "data.linux.id", "var.aws_ami.linux"], 1, "Los data sources llevan el prefijo `data.`."),
 ("¿Cuándo necesitas `depends_on`?",
  ["Siempre que un recurso use otro", "Cuando hay una dependencia real que no se expresa con ninguna referencia", "Para acelerar el apply", "Nunca, está obsoleto"], 1,
  "Las referencias ya crean dependencias implícitas; `depends_on` es para las ocultas."),
 ("El security group y la AMI no se referencian entre sí. ¿Cómo los procesa Terraform?",
  ["Uno detrás de otro, por orden alfabético", "En paralelo", "Primero el que esté antes en el archivo", "Da error"], 1,
  "Los nodos independientes del grafo se ejecutan en paralelo (hasta `-parallelism`, 10 por defecto)."),
 ("¿Por qué usar un data source para la AMI en lugar de escribir su ID?",
  ["Porque es obligatorio", "Porque los IDs cambian por región y por versión", "Porque es más barato", "Porque así la instancia es más rápida"], 1,
  "El data source busca la imagen adecuada en cada región y momento."),
 ("En el plan ves `~ instance_type = \"t3.micro\" -> \"t3.small\"`. ¿Qué pasará?",
  ["Se destruye la instancia", "Se modifica la instancia existente", "No pasa nada", "Se crea una segunda instancia"], 1,
  "`~` es update in-place: AWS cambia el tamaño parando y arrancando la misma instancia."),
]

RETOS = [
 {"titulo": "Abre HTTPS y saca más outputs",
  "enunciado": "Añade una regla de entrada para el puerto 443 y outputs con el ID de la instancia, su zona de disponibilidad y el nombre de la AMI usada.",
  "pista": "Copia la regla `http` cambiando nombre y puertos. La AMI expone el atributo `name`.",
  "solucion": ("hcl", """resource "aws_vpc_security_group_ingress_rule" "https" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
}

output "detalles" {
  value = {
    id   = aws_instance.web.id
    zona = aws_instance.web.availability_zone
    ami  = data.aws_ami.amazon_linux.name
  }
}""")},
 {"titulo": "Tu propia red (VPC)",
  "enunciado": "En vez de la VPC por defecto, crea una VPC `10.0.0.0/16` con una subred pública `10.0.1.0/24`, un internet gateway y una tabla de rutas con salida a Internet. Lanza la instancia en esa subred con IP pública.",
  "pista": "Recursos: `aws_vpc`, `aws_subnet` (con `map_public_ip_on_launch = true`), `aws_internet_gateway`, `aws_route_table`, `aws_route_table_association`. El security group necesita `vpc_id`.",
  "solucion": ("hcl", """resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags                 = { Name = "curso-vpc" }
}

resource "aws_subnet" "publica" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.disponibles.names[0]
  map_public_ip_on_launch = true
  tags                    = { Name = "curso-publica" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "publica" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "publica" {
  subnet_id      = aws_subnet.publica.id
  route_table_id = aws_route_table.publica.id
}

data "aws_availability_zones" "disponibles" {
  state = "available"
}

# En el security group añade:   vpc_id = aws_vpc.main.id
# En la instancia añade:        subnet_id = aws_subnet.publica.id""")},
]
