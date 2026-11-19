# -*- coding: utf-8 -*-
# Módulo 15 · Variables, facts y plantillas

LECCION = [
 ("h", "Variables"),
 ("p", "Como en Terraform, las **variables** sirven para no escribir los datos dentro de las tareas. Se usan escribiendo su nombre entre dobles llaves: `{{ nombre }}`."),
 ("code", "yaml", "playbook con variables", """---
- name: Ejemplo de variables
  hosts: local
  vars:
    carpeta: /tmp/miweb
    saludo: "Hola desde Ansible"

  tasks:
    - name: Crear la carpeta
      ansible.builtin.file:
        path: "{{ carpeta }}"
        state: directory
        mode: "0755"

    - name: Escribir el saludo
      ansible.builtin.copy:
        content: "{{ saludo }}"
        dest: "{{ carpeta }}/saludo.txt"
        mode: "0644\""""),
 ("warn", "Si un valor **empieza** por `{{`, ponlo entre comillas: `path: \"{{ carpeta }}\"`. Si no, YAML da error."),

 ("h", "Dónde poner las variables"),
 ("p", "Lo más ordenado es guardarlas en la carpeta **group_vars**, junto al inventario. Ansible las carga solas según el grupo:"),
 ("code", "text", "estructura", """inventario/
├── hosts.ini
└── group_vars/
    ├── all.yml      # variables para todos los servidores
    └── web.yml      # variables solo para el grupo web"""),
 ("code", "yaml", "inventario/group_vars/all.yml", """---
web_nombre: "Ana García"
web_descripcion: "Aprendiendo Terraform y Ansible."
web_proyectos:
  - nombre: "Infraestructura con Terraform"
    descripcion: "Red y servidores en AWS."
  - nombre: "Configuración con Ansible"
    descripcion: "Servidores configurados solos.\""""),
 ("p", "También puedes dar una variable al ejecutar. Esta forma gana a todas las demás:"),
 ("term", """$ ansible-playbook site.yml -e "web_nombre=Luis\""""),
 ("table", ["Dónde", "Prioridad"], [
  ["`defaults/` de un rol (módulo 17)", "La más baja"],
  ["`group_vars/all.yml`", "Baja"],
  ["`group_vars/GRUPO.yml`", "Media"],
  ["`vars:` en el playbook", "Alta"],
  ["`-e` al ejecutar", "La más alta"],
 ]),

 ("h", "Facts: lo que Ansible sabe de cada servidor"),
 ("p", "Al empezar un playbook, Ansible recoge información de cada servidor: nombre, sistema operativo, IP, memoria... Son los **facts** (*hechos*). Es la tarea `Gathering Facts` que ves al principio."),
 ("term", """$ ansible web1 -m setup -a "filter=ansible_distribution*"
web1 | SUCCESS => {
    "ansible_facts": {
        "ansible_distribution": "Ubuntu",
        "ansible_distribution_version": "24.04"
    }
}"""),
 ("p", "Se usan con `ansible_facts['nombre']` (sin el prefijo `ansible_`):"),
 ("table", ["Fact", "Ejemplo"], [
  ["`ansible_facts['hostname']`", "ip-10-0-1-25"],
  ["`ansible_facts['distribution']`", "Ubuntu"],
  ["`ansible_facts['distribution_version']`", "24.04"],
  ["`ansible_facts['default_ipv4']['address']`", "10.0.1.25"],
  ["`ansible_facts['memtotal_mb']`", "957"],
 ]),
 ("p", "Y hay variables especiales que siempre existen, como `inventory_hostname`: el nombre del servidor en el inventario (web1, web2)."),

 ("h", "Plantillas Jinja2"),
 ("p", "Una **plantilla** es un archivo con huecos que Ansible rellena con variables. Se escriben en el lenguaje **Jinja2** y por costumbre terminan en `.j2`:"),
 ("code", "text", "templates/index.html.j2", """<h1>{{ web_nombre }}</h1>
<p>{{ web_descripcion }}</p>
<p>Servidor: {{ inventory_hostname }} ({{ ansible_facts['distribution'] }})</p>"""),
 ("p", "El módulo `template` rellena la plantilla y deja el resultado en el servidor:"),
 ("code", "yaml", "tarea", """    - name: Generar la página principal
      ansible.builtin.template:
        src: templates/index.html.j2
        dest: /var/www/miweb/index.html
        mode: "0644\""""),
 ("p", "Resultado en web1:"),
 ("code", "text", "/var/www/miweb/index.html", """<h1>Ana García</h1>
<p>Aprendiendo Terraform y Ansible.</p>
<p>Servidor: web1 (Ubuntu)</p>"""),

 ("h", "Bucles y condiciones en las plantillas"),
 ("p", "Jinja2 permite recorrer listas con `{% for %}` y elegir con `{% if %}`:"),
 ("code", "text", "templates/index.html.j2", """<ul>
{% for proyecto in web_proyectos %}
  <li><strong>{{ proyecto.nombre }}</strong>: {{ proyecto.descripcion }}</li>
{% endfor %}
</ul>

{% if web_proyectos | length > 2 %}
<p>Tengo muchos proyectos.</p>
{% endif %}"""),
 ("ul", [
  "`{{ }}` muestra un valor.",
  "`{% %}` es lógica: bucles y condiciones.",
  "`|` aplica un **filtro**: `| length` (cuántos hay), `| upper` (mayúsculas), `| default('nada')` (valor si no existe).",
 ]),
]

TEST = [
 ("¿Cómo se usa la variable `carpeta` dentro de una tarea?",
  ["$carpeta", "{{ carpeta }}", "var.carpeta", "${carpeta}"], 1, "Ansible usa la sintaxis de Jinja2: dobles llaves."),
 ("¿Por qué hay que escribir `path: \"{{ carpeta }}\"` con comillas?",
  ["Por estética", "Porque si el valor empieza por {{ YAML lo confunde y da error", "Porque es un número", "No hace falta"], 1,
  "YAML interpreta { como el inicio de un diccionario."),
 ("¿Dónde pondrías variables comunes a todos los servidores?",
  ["En group_vars/all.yml", "En el inventario dentro de [web]", "En ansible.cfg", "En el estado"], 0,
  "group_vars/all.yml se aplica a todos los servidores."),
 ("¿Qué son los facts?",
  ["Errores de Ansible", "Datos que Ansible recoge de cada servidor", "Variables cifradas", "Tareas especiales"], 1,
  "Nombre, sistema, IP, memoria... se recogen al empezar el playbook."),
 ("¿Qué variable tiene el nombre del servidor en el inventario?",
  ["hostname", "inventory_hostname", "server_name", "ansible_host"], 1,
  "`ansible_host` es la IP; `inventory_hostname` es el nombre (web1, web2)."),
 ("¿Para qué sirve `{% for %}` en una plantilla?",
  ["Para comentar", "Para recorrer una lista", "Para cargar un archivo", "Para cifrar"], 1,
  "Repite una parte de la plantilla por cada elemento."),
 ("Tienes `web_nombre` en group_vars y ejecutas con `-e web_nombre=Luis`. ¿Qué valor se usa?",
  ["El de group_vars", "Luis", "Ninguno", "Da error"], 1, "Las variables con -e tienen la prioridad más alta."),
]

RETOS = [
 {"titulo": "Archivo de configuración con plantilla",
  "enunciado": "Crea una plantilla `app.conf.j2` que genere un archivo con el nombre del servidor, el sistema operativo y una línea por cada puerto de la lista `puertos: [80, 443, 8080]`. Genera el archivo en `/tmp/app.conf`.",
  "pista": "Usa `inventory_hostname`, `ansible_facts['distribution']` y un `{% for %}`.",
  "solucion": ("text", """# templates/app.conf.j2
servidor = {{ inventory_hostname }}
sistema  = {{ ansible_facts['distribution'] }}
{% for puerto in puertos %}
puerto = {{ puerto }}
{% endfor %}

# playbook
- name: Configuración
  hosts: local
  vars:
    puertos: [80, 443, 8080]
  tasks:
    - name: Generar app.conf
      ansible.builtin.template:
        src: templates/app.conf.j2
        dest: /tmp/app.conf
        mode: "0644\"""")},
 {"titulo": "Valor por defecto",
  "enunciado": "Haz que la plantilla muestre «Sin descripción» si la variable `web_descripcion` no existe.",
  "pista": "Hay un filtro para eso.",
  "solucion": ("text", """<p>{{ web_descripcion | default('Sin descripción') }}</p>""")},
]

PROYECTO = {
 "titulo": "Tu web personal con plantillas",
 "bloques": [
  ("p", "Vas a sustituir la página de prueba por tu web personal: tu nombre, una descripción y tus proyectos. Y añadirás una página de estado que muestra los datos de cada servidor."),
  ("p", "1. Crea las variables con tus datos (cámbialos por los tuyos):"),
  ("code", "yaml", "ansible/inventario/group_vars/all/web.yml", """---
web_nombre: "Ana García"
web_titulo: "Mi web en la nube"
web_descripcion: "Aprendiendo Terraform y Ansible paso a paso."
web_proyectos:
  - nombre: "Infraestructura con Terraform"
    descripcion: "Red, servidores y firewall en AWS creados con código."
  - nombre: "Configuración con Ansible"
    descripcion: "Servidores configurados automáticamente."
  - nombre: "Despliegue automático"
    descripcion: "Un solo comando crea y configura todo.\""""),
  ("info", "`group_vars/all/` es una carpeta: Ansible carga todos los archivos `.yml` que haya dentro. Así podrás añadir más archivos de variables (en el paso del módulo 18 añadirás uno cifrado)."),
  ("p", "2. Crea la plantilla de la página principal:"),
  ("code", "text", "ansible/templates/index.html.j2", """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>{{ web_titulo }}</title>
</head>
<body>
  <h1>{{ web_nombre }}</h1>
  <p>{{ web_descripcion }}</p>
  <h2>Proyectos</h2>
  <ul>
{% for proyecto in web_proyectos %}
    <li><strong>{{ proyecto.nombre }}</strong>: {{ proyecto.descripcion }}</li>
{% endfor %}
  </ul>
  <p>Servido por {{ inventory_hostname }}. <a href="/estado.html">Estado del servidor</a></p>
</body>
</html>"""),
  ("p", "3. Crea la página de estado con los facts:"),
  ("code", "text", "ansible/templates/estado.html.j2", """<!doctype html>
<html lang="es">
<head><meta charset="utf-8"><title>Estado de {{ inventory_hostname }}</title></head>
<body>
  <h1>Estado del servidor</h1>
  <ul>
    <li>Nombre: {{ inventory_hostname }} ({{ ansible_facts['hostname'] }})</li>
    <li>Sistema: {{ ansible_facts['distribution'] }} {{ ansible_facts['distribution_version'] }}</li>
    <li>IP privada: {{ ansible_facts['default_ipv4']['address'] | default('desconocida') }}</li>
    <li>Memoria: {{ ansible_facts['memtotal_mb'] }} MB</li>
  </ul>
  <p><a href="/">Volver</a></p>
</body>
</html>"""),
  ("p", "4. En `site.yml`, sustituye la tarea «Publicar una página de prueba» por estas dos:"),
  ("code", "yaml", "ansible/site.yml (tareas nuevas)", """    - name: Generar la página principal
      ansible.builtin.template:
        src: templates/index.html.j2
        dest: /var/www/html/index.html
        mode: "0644"

    - name: Generar la página de estado
      ansible.builtin.template:
        src: templates/estado.html.j2
        dest: /var/www/html/estado.html
        mode: "0644\""""),
  ("term", """$ ansible-playbook site.yml
...
TASK [Generar la página principal] ********************************
changed: [web1]
changed: [web2]
$ curl -s http://54.170.10.21/estado.html | grep Nombre
    <li>Nombre: web2 (ip-10-0-1-187)</li>"""),
  ("p", "Resultado de este paso: tu web personal está en internet y cada servidor muestra sus propios datos en `/estado.html`."),
 ],
}
