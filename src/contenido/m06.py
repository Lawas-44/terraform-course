# -*- coding: utf-8 -*-
# Módulo 06 · Recursos, data sources y dependencias

LECCION = [
 ("h", "Lo que escribes y lo que recibes"),
 ("p", "Cada recurso tiene dos clases de datos:"),
 ("ul", [
  "**Argumentos**: lo que tú escribes. Por ejemplo, el tamaño del servidor: `instance_type = \"t3.micro\"`.",
  "**Atributos**: lo que AWS te devuelve al crearlo. Por ejemplo, su IP pública: `public_ip`.",
 ]),
 ("p", "Por eso en el plan algunos valores aparecen como `(known after apply)`: AWS los decide al crear el recurso."),
 ("info", "En este módulo creamos un servidor pequeño (`t3.micro`), gratis en la capa gratuita de AWS. Bórralo siempre al terminar."),

 ("h", "Consultar cosas que ya existen: data"),
 ("p", "Un bloque `data` **no crea nada**: solo busca información. Por ejemplo, la imagen de sistema operativo más reciente para un servidor:"),
 ("code", "hcl", "data.tf", """data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}"""),
 ("p", "Se usa con el prefijo `data.`: `data.aws_ami.amazon_linux.id`."),
 ("p", "¿Por qué no escribir el código de la imagen directamente? Porque cambia según la región y cada pocas semanas sale una versión nueva. Así siempre usas la correcta."),

 ("h", "El orden lo decide Terraform"),
 ("p", "Cuando un recurso usa datos de otro, Terraform sabe que debe crearlo después. Con eso calcula el orden y crea **a la vez** lo que no depende entre sí."),
 ("code", "text", "orden en el ejemplo de este módulo", """imagen (data)  ──────┐
                     ├──>  servidor
firewall  ───────────┘
   └──> reglas del firewall"""),
 ("p", "Al borrar, el orden es el contrario: primero el servidor y después el firewall."),
 ("p", "Si hay una dependencia que Terraform no puede ver (porque no hay ninguna referencia), puedes indicarla con `depends_on`. Úsalo solo cuando sea necesario:"),
 ("code", "hcl", "depends_on", """resource "aws_instance" "app" {
  # ...
  depends_on = [aws_s3_bucket.logs]
}"""),

 ("h", "Práctica: un servidor web"),
 ("p", "Vamos a crear un servidor con una página web. Necesitamos tres cosas: la imagen del sistema, un **firewall** (en AWS se llama *security group*) y el **servidor** (en AWS, *instancia EC2*)."),
 ("code", "hcl", "main.tf", """provider "aws" {
  region = "eu-west-1"
}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

# Firewall
resource "aws_security_group" "web" {
  name_prefix = "web-"
  description = "Permite HTTP"
}

# Regla: dejar entrar visitas web (puerto 80)
resource "aws_vpc_security_group_ingress_rule" "http" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 80
  to_port           = 80
  ip_protocol       = "tcp"
}

# Regla: dejar salir todo (para descargar programas)
resource "aws_vpc_security_group_egress_rule" "todo" {
  security_group_id = aws_security_group.web.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

# Servidor
resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  vpc_security_group_ids = [aws_security_group.web.id]

  # Script que se ejecuta al arrancar: instala un servidor web
  user_data = <<-EOF
    #!/bin/bash
    dnf install -y nginx
    echo "<h1>Hola desde Terraform</h1>" > /usr/share/nginx/html/index.html
    systemctl enable --now nginx
  EOF

  user_data_replace_on_change = true

  tags = {
    Name = "web-curso-terraform"
  }
}

output "url" {
  value = "http://${aws_instance.web.public_ip}"
}"""),
 ("term", """$ terraform init
$ terraform apply
...
Plan: 4 to add, 0 to change, 0 to destroy.
...
aws_security_group.web: Creation complete after 2s
aws_instance.web: Creation complete after 13s

Outputs:
url = "http://54.170.10.20"

$ curl http://54.170.10.20
<h1>Hola desde Terraform</h1>"""),
 ("tip", "El servidor tarda uno o dos minutos en instalar la web. Si al principio no carga, espera un poco."),

 ("h", "Modificar o recrear"),
 ("p", "Cambia algo y mira el plan antes de aplicar. Algunos cambios se hacen sobre el mismo recurso (`~`) y otros obligan a borrarlo y crearlo de nuevo (`-/+`):"),
 ("table", ["Cambio", "Qué pasa"], [
  ["Cambiar la etiqueta `Name`", "Se modifica (`~`)"],
  ["Cambiar `instance_type` a `t3.small`", "Se modifica (`~`); el servidor se reinicia"],
  ["Cambiar `user_data`", "Se borra y se crea de nuevo (`-/+`)"],
  ["Cambiar la imagen (`ami`)", "Se borra y se crea de nuevo (`-/+`)"],
 ]),
 ("warn", "Si un servidor se recrea, pierde todo lo que tenía en su disco y cambia de IP."),

 ("h", "Ver lo que se ha creado"),
 ("term", """$ terraform state list
data.aws_ami.amazon_linux
aws_instance.web
aws_security_group.web
aws_vpc_security_group_egress_rule.todo
aws_vpc_security_group_ingress_rule.http
$ terraform state show aws_instance.web"""),
 ("p", "Cuando termines, borra todo:"),
 ("term", """$ terraform destroy"""),
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


PROYECTO = {'titulo': 'Tu primer servidor',
 'bloques': [('p',
              'Vas a crear un servidor Ubuntu en AWS, un firewall que solo deja entrar por SSH desde tu IP y '
              'la clave SSH para entrar.'),
             ('code',
              'hcl',
              'terraform/main.tf',
              '# Imagen más reciente de Ubuntu 24.04\n'
              'data "aws_ami" "ubuntu" {\n'
              '  most_recent = true\n'
              '  owners      = ["099720109477"] # Canonical, la empresa de Ubuntu\n'
              '\n'
              '  filter {\n'
              '    name   = "name"\n'
              '    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]\n'
              '  }\n'
              '}\n'
              '\n'
              '# Tu clave SSH pública, subida a AWS\n'
              'resource "aws_key_pair" "this" {\n'
              '  key_name   = "${local.prefijo}-clave"\n'
              '  public_key = file(pathexpand(var.ruta_clave_publica))\n'
              '}\n'
              '\n'
              '# Firewall\n'
              'resource "aws_security_group" "web" {\n'
              '  name_prefix = "${local.prefijo}-web-"\n'
              '  description = "SSH desde mi IP y HTTP desde Internet"\n'
              '}\n'
              '\n'
              'resource "aws_vpc_security_group_ingress_rule" "ssh" {\n'
              '  security_group_id = aws_security_group.web.id\n'
              '  cidr_ipv4         = var.mi_ip\n'
              '  from_port         = 22\n'
              '  to_port           = 22\n'
              '  ip_protocol       = "tcp"\n'
              '}\n'
              '\n'
              'resource "aws_vpc_security_group_ingress_rule" "http" {\n'
              '  security_group_id = aws_security_group.web.id\n'
              '  cidr_ipv4         = "0.0.0.0/0"\n'
              '  from_port         = 80\n'
              '  to_port           = 80\n'
              '  ip_protocol       = "tcp"\n'
              '}\n'
              '\n'
              'resource "aws_vpc_security_group_egress_rule" "todo" {\n'
              '  security_group_id = aws_security_group.web.id\n'
              '  cidr_ipv4         = "0.0.0.0/0"\n'
              '  ip_protocol       = "-1"\n'
              '}\n'
              '\n'
              '# El servidor\n'
              'resource "aws_instance" "web" {\n'
              '  ami                    = data.aws_ami.ubuntu.id\n'
              '  instance_type          = "t3.micro"\n'
              '  key_name               = aws_key_pair.this.key_name\n'
              '  vpc_security_group_ids = [aws_security_group.web.id]\n'
              '\n'
              '  metadata_options {\n'
              '    http_tokens = "required" # medida de seguridad recomendada\n'
              '  }\n'
              '\n'
              '  root_block_device {\n'
              '    encrypted = true # disco cifrado\n'
              '  }\n'
              '\n'
              '  tags = {\n'
              '    Name = "${local.prefijo}-web1"\n'
              '    Rol  = "web"\n'
              '  }\n'
              '}'),
             ('code',
              'hcl',
              'terraform/outputs.tf',
              'output "ip" {\n  value = aws_instance.web.public_ip\n}'),
             ('term',
              '$ terraform plan\n'
              'Plan: 6 to add, 0 to change, 0 to destroy.\n'
              '$ terraform apply\n'
              '...\n'
              'Outputs:\n'
              'ip = "54.170.10.20"\n'
              '$ ssh ubuntu@54.170.10.20\n'
              'Welcome to Ubuntu 24.04 LTS\n'
              'ubuntu@ip-172-31-5-10:~$ exit'),
             ('info',
              'De momento el servidor usa la red por defecto de AWS. En el paso del módulo 11 crearás tu '
              'propia red.'),
             ('warn',
              'A partir de aquí tienes un servidor encendido. Si terminas la sesión, ejecuta `terraform '
              'destroy`; en la siguiente, `terraform apply` lo vuelve a crear igual.'),
             ('p', 'Resultado de este paso: tienes un servidor en AWS y puedes entrar en él por SSH.')]}
