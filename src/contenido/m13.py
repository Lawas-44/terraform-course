# -*- coding: utf-8 -*-
# Módulo 13 · Introducción a Ansible

LECCION = [
 ("h", "Qué es Ansible"),
 ("p", "Con Terraform ya sabes **crear** servidores. Pero un servidor recién creado está vacío: no tiene tu web, ni nginx, ni nada configurado. **Ansible** se encarga de eso: entra en los servidores y los **configura** (instala programas, copia archivos, arranca servicios...)."),
 ("table", ["", "Terraform", "Ansible"], [
  ["Para qué", "Crear infraestructura: redes, servidores, firewalls", "Configurar lo que hay dentro de los servidores"],
  ["Cómo trabaja", "Habla con la API de la nube", "Entra en los servidores por SSH"],
  ["Lenguaje", "HCL (archivos `.tf`)", "YAML (archivos `.yml`)"],
  ["Recuerda lo que hizo", "Sí, en el estado", "No: cada vez mira cómo está el servidor"],
 ]),
 ("p", "Por eso se usan juntos: **Terraform crea los servidores y Ansible los configura**."),

 ("h", "Cómo funciona"),
 ("ul", [
  "Ansible se instala **solo en tu ordenador** (el *nodo de control*). En los servidores no hay que instalar nada.",
  "Se conecta a cada servidor por **SSH**, igual que harías tú a mano.",
  "En los servidores solo necesita que haya Python, que ya viene en casi todos los Linux.",
 ]),
 ("code", "text", "esquema", """   Tu ordenador (Ansible)
          |
          |  SSH
    +-----+------+
    |            |
    v            v
  web1         web2"""),

 ("h", "Instalar Ansible"),
 ("p", "Ansible funciona en Linux y macOS. En Windows se usa dentro de **WSL** (lo instalaste en el módulo 1)."),
 ("code", "bash", "macOS", "brew install ansible"),
 ("code", "bash", "Ubuntu / Debian / WSL", """sudo apt update
sudo apt install -y pipx
pipx install --include-deps ansible
pipx ensurepath"""),
 ("term", """$ ansible --version
ansible [core 2.18.1]
  python version = 3.12.3"""),

 ("h", "El inventario: la lista de servidores"),
 ("p", "Ansible necesita saber a qué servidores conectarse. Esa lista se llama **inventario** y es un archivo de texto. Los servidores se agrupan con un nombre entre corchetes:"),
 ("code", "text", "inventario.ini", """[web]
web1 ansible_host=54.170.10.20
web2 ansible_host=54.170.10.21

[web:vars]
ansible_user=ubuntu"""),
 ("ul", [
  "`[web]` es un **grupo**. Puedes tener varios: `[web]`, `[basedatos]`...",
  "`web1` es el nombre que tú le das; `ansible_host` es su IP.",
  "`[web:vars]` define variables para todo el grupo. `ansible_user` es el usuario con el que entra por SSH (en Ubuntu de AWS es `ubuntu`).",
  "Existe siempre el grupo especial `all`, que incluye a todos los servidores.",
 ]),
 ("term", """$ ansible-inventory -i inventario.ini --graph
@all:
  |--@ungrouped:
  |--@web:
  |  |--web1
  |  |--web2"""),

 ("h", "El archivo ansible.cfg"),
 ("p", "Para no repetir opciones en cada comando, se crea un archivo `ansible.cfg` en la carpeta del proyecto. Ansible lo lee solo:"),
 ("code", "text", "ansible.cfg", """[defaults]
inventory = inventario.ini
host_key_checking = False"""),
 ("p", "Con esto ya no hace falta escribir `-i inventario.ini`. `host_key_checking = False` evita que Ansible pregunte si confías en cada servidor la primera vez (útil mientras aprendes)."),

 ("h", "Comandos ad-hoc"),
 ("p", "Un comando **ad-hoc** es una orden suelta que se ejecuta en varios servidores a la vez. Sirve para comprobaciones rápidas. La forma es: `ansible GRUPO -m MÓDULO -a \"OPCIONES\"`."),
 ("p", "El primero que siempre se prueba es `ping`. No es un ping de red: comprueba que Ansible puede entrar y usar Python:"),
 ("term", """$ ansible web -m ping
web1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
web2 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}"""),
 ("p", "Más ejemplos:"),
 ("term", """$ ansible web -a "uptime"
web1 | CHANGED | rc=0 >>
 10:15:01 up 12 min,  1 user,  load average: 0.00, 0.01, 0.00
web2 | CHANGED | rc=0 >>
 10:15:01 up 12 min,  1 user,  load average: 0.02, 0.03, 0.00
$ ansible web -b -m apt -a "name=htop state=present update_cache=true\""""),
 ("ul", [
  "`-a \"uptime\"`: ejecuta un comando de Linux.",
  "`-m apt`: usa el **módulo** `apt` para instalar un paquete.",
  "`-b` (*become*): ejecuta como administrador, como `sudo`.",
 ]),
 ("info", "Un **módulo** es una acción ya preparada: instalar un paquete (`apt`), copiar un archivo (`copy`), arrancar un servicio (`service`)... Ansible trae cientos."),

 ("h", "Practicar sin servidores"),
 ("p", "Para practicar sin crear nada en AWS puedes usar **tu propio ordenador** como servidor. Se indica con `ansible_connection=local`:"),
 ("code", "text", "inventario.ini", """[local]
localhost ansible_connection=local"""),
 ("term", """$ ansible local -m ping
localhost | SUCCESS => {
    "changed": false,
    "ping": "pong"
}"""),
 ("tip", "Los labs de Ansible del curso usan este inventario local, así que puedes hacerlos sin coste. En el proyecto guiado usarás los servidores de AWS que creaste con Terraform."),
]

TEST = [
 ("¿Qué hace Ansible?",
  ["Crea redes y servidores en la nube", "Configura lo que hay dentro de los servidores", "Guarda el estado de Terraform", "Es un editor de código"], 1,
  "Ansible instala programas, copia archivos y arranca servicios en servidores que ya existen."),
 ("¿Cómo se conecta Ansible a los servidores Linux?",
  ["Con un agente instalado en cada servidor", "Por SSH", "Por la API de AWS", "Por correo"], 1,
  "No hay que instalar nada en los servidores: Ansible entra por SSH."),
 ("¿Qué es el inventario?",
  ["La lista de paquetes instalados", "La lista de servidores a los que se conecta Ansible", "El estado de Ansible", "Un tipo de módulo"], 1,
  "Es un archivo con los servidores, agrupados por nombre."),
 ("¿Qué significa `-b` en `ansible web -b -m apt -a \"name=htop\"`?",
  ["Que se ejecute en segundo plano", "Que se ejecute como administrador (become)", "Que haga una copia de seguridad", "Que se ejecute en todos los grupos"], 1,
  "`-b` equivale a usar sudo en el servidor."),
 ("¿Qué comprueba `ansible all -m ping`?",
  ["La velocidad de la red", "Que Ansible puede entrar en los servidores y usar Python", "Que el puerto 80 está abierto", "Que los servidores tienen Internet"], 1,
  "Si responde pong, Ansible puede trabajar con ese servidor."),
 ("¿Dónde se instala Ansible?",
  ["En cada servidor", "Solo en el ordenador desde el que lo ejecutas", "En AWS", "En GitHub"], 1,
  "Por eso se dice que Ansible no usa agentes (es *agentless*)."),
]

RETOS = [
 {"titulo": "Tu primer inventario",
  "enunciado": "Crea un inventario con dos grupos: `web` (con localhost) y `basedatos` (vacío). Comprueba la estructura con `ansible-inventory --graph` y haz `ping` al grupo web.",
  "pista": "Un grupo vacío se declara solo con su nombre entre corchetes.",
  "solucion": ("text", """# inventario.ini
[web]
localhost ansible_connection=local

[basedatos]

# Comandos:
# ansible-inventory -i inventario.ini --graph
# ansible -i inventario.ini web -m ping""")},
 {"titulo": "Información del sistema",
  "enunciado": "Con un comando ad-hoc, muestra la versión del sistema operativo de tu máquina usando el módulo `setup` y un filtro.",
  "pista": "Los datos que empiezan por `ansible_distribution` contienen el nombre y la versión.",
  "solucion": ("bash", """ansible local -m setup -a "filter=ansible_distribution*"
# localhost | SUCCESS => {
#     "ansible_facts": {
#         "ansible_distribution": "Ubuntu",
#         "ansible_distribution_version": "24.04",
#         ...""")},
]

PROYECTO = {
 "titulo": "Conecta Ansible con tus servidores",
 "bloques": [
  ("p", "Ya tienes dos servidores en AWS creados con Terraform y un inventario que Terraform genera solo (paso del módulo 8). Ahora vas a comprobar que Ansible puede entrar en ellos."),
  ("p", "Primero, levanta la infraestructura si la habías destruido:"),
  ("term", """$ cd terraform
$ terraform apply
$ cat ../ansible/inventario/hosts.ini
# Archivo generado por Terraform. No lo edites a mano.
[web]
web1 ansible_host=54.170.10.20
web2 ansible_host=54.170.10.21

[web:vars]
ansible_user=ubuntu"""),
  ("p", "Crea el archivo de configuración de Ansible en la carpeta `ansible/`:"),
  ("code", "text", "ansible/ansible.cfg", """[defaults]
inventory = inventario/hosts.ini
roles_path = roles
host_key_checking = False
interpreter_python = auto_silent

[ssh_connection]
pipelining = True"""),
  ("p", "Comprueba la conexión y prueba algunos comandos:"),
  ("term", """$ cd ../ansible
$ ansible web -m ping
web1 | SUCCESS => { "ping": "pong" }
web2 | SUCCESS => { "ping": "pong" }
$ ansible web -a "hostname"
web1 | CHANGED | rc=0 >>
ip-10-0-1-25
web2 | CHANGED | rc=0 >>
ip-10-0-1-187"""),
  ("info", "Ansible usa tu clave SSH de `~/.ssh/` automáticamente. Es la misma clave pública que Terraform subió a AWS en el paso del módulo 6."),
  ("p", "Resultado de este paso: Ansible llega a tus dos servidores. En el siguiente módulo los configurarás."),
 ],
}
