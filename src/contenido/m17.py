# -*- coding: utf-8 -*-
# Módulo 17 · Roles y colecciones

LECCION = [
 ("h", "Qué es un rol"),
 ("p", "Cuando un playbook crece, se vuelve difícil de leer. Un **rol** es una forma de ordenar tareas, plantillas, archivos y handlers en carpetas, para reutilizarlos. Es el equivalente a los **módulos de Terraform**."),
 ("p", "Por ejemplo, un rol `nginx` instala y configura nginx. Lo puedes usar en todos tus proyectos."),

 ("h", "Estructura de un rol"),
 ("p", "Un rol es una carpeta dentro de `roles/` con subcarpetas de nombres fijos. Ansible sabe qué hay en cada una:"),
 ("code", "text", "roles/nginx/", """roles/
└── nginx/
    ├── tasks/
    │   └── main.yml       # las tareas
    ├── handlers/
    │   └── main.yml       # los handlers
    ├── templates/
    │   └── sitio.conf.j2  # plantillas
    ├── files/             # archivos que se copian tal cual
    └── defaults/
        └── main.yml       # valores por defecto de las variables"""),
 ("p", "Puedes crear esta estructura con un comando:"),
 ("term", """$ ansible-galaxy role init roles/nginx
- Role roles/nginx was created successfully"""),
 ("info", "Solo hace falta crear las carpetas que vayas a usar. Las vacías se pueden borrar."),

 ("h", "Dentro de un rol"),
 ("p", "`tasks/main.yml` contiene solo la lista de tareas, sin `hosts` ni `become`:"),
 ("code", "yaml", "roles/nginx/tasks/main.yml", """---
- name: Instalar nginx
  ansible.builtin.apt:
    name: nginx
    state: present

- name: Configurar el sitio
  ansible.builtin.template:
    src: sitio.conf.j2
    dest: /etc/nginx/sites-available/miweb
    mode: "0644"
  notify: Recargar nginx"""),
 ("p", "Fíjate en `src: sitio.conf.j2`: dentro de un rol no hace falta poner la ruta `templates/`, Ansible la busca sola en la carpeta del rol."),
 ("code", "yaml", "roles/nginx/defaults/main.yml", """---
nginx_raiz: /var/www/miweb"""),
 ("p", "En `defaults/` van las variables que quien use el rol puede cambiar. Tienen la prioridad más baja, así que cualquier otra variable las sustituye."),
 ("tip", "Es buena costumbre que las variables de un rol empiecen por el nombre del rol (`nginx_raiz`, `nginx_puerto`). Así no se mezclan con las de otros roles."),

 ("h", "Usar roles en un playbook"),
 ("p", "El playbook queda muy corto: solo dice qué roles aplicar y en qué servidores:"),
 ("code", "yaml", "site.yml", """---
- name: Configurar los servidores web
  hosts: web
  become: true
  roles:
    - comun
    - nginx
    - web"""),
 ("p", "Los roles se ejecutan en orden. Ansible los busca en la carpeta `roles/` junto al playbook (o en `roles_path` de `ansible.cfg`)."),

 ("h", "Roles y colecciones de otros: Ansible Galaxy"),
 ("p", "**Ansible Galaxy** (galaxy.ansible.com) es como el Registry de Terraform: hay miles de roles y **colecciones** hechos por otros."),
 ("ul", [
  "Una **colección** es un paquete de módulos y roles. Por ejemplo, `community.general` añade cientos de módulos, y `amazon.aws` añade módulos para AWS.",
  "Los módulos que has usado (`ansible.builtin.apt`...) vienen en la colección `ansible.builtin`, que ya está instalada.",
 ]),
 ("term", """$ ansible-galaxy collection install community.general
$ ansible-galaxy collection list | grep community.general
community.general    10.1.0"""),
 ("p", "Para que todo el equipo instale lo mismo, se listan en un archivo `requirements.yml`:"),
 ("code", "yaml", "requirements.yml", """---
collections:
  - name: community.general
    version: ">=10.0.0"
  - name: amazon.aws"""),
 ("term", """$ ansible-galaxy install -r requirements.yml"""),
 ("warn", "Como con los módulos de Terraform, lee el código de un rol antes de usarlo y fija la versión."),
]

TEST = [
 ("¿A qué se parece un rol de Ansible en Terraform?",
  ["Al estado", "A un módulo", "A un provider", "A un output"], 1, "Ambos agrupan código para reutilizarlo."),
 ("¿En qué archivo van las tareas de un rol?",
  ["roles/nginx/main.yml", "roles/nginx/tasks/main.yml", "roles/nginx/site.yml", "roles/tasks/nginx.yml"], 1,
  "Cada tipo de contenido va en su carpeta, siempre con main.yml."),
 ("¿Para qué sirve la carpeta `defaults/` de un rol?",
  ["Para las plantillas", "Para los valores por defecto de las variables, que se pueden cambiar desde fuera", "Para los handlers", "Para los tests"], 1,
  "Tienen la prioridad más baja de todas."),
 ("Dentro de un rol, ¿cómo indicas la plantilla `templates/sitio.conf.j2`?",
  ["src: roles/nginx/templates/sitio.conf.j2", "src: sitio.conf.j2", "src: templates/sitio.conf.j2", "template: sitio"], 1,
  "Ansible busca sola en la carpeta templates del rol."),
 ("¿Qué comando crea la estructura de un rol?",
  ["ansible-role new nginx", "ansible-galaxy role init roles/nginx", "ansible-playbook --init", "mkdir role"], 1, ""),
 ("¿Para qué sirve `requirements.yml`?",
  ["Para listar los servidores", "Para listar los roles y colecciones que hay que instalar", "Para guardar contraseñas", "Para configurar SSH"], 1,
  "Se instalan con `ansible-galaxy install -r requirements.yml`."),
]

RETOS = [
 {"titulo": "Crea tu rol",
  "enunciado": "Convierte el playbook del reto del módulo 14 (carpeta `/tmp/miweb` con `index.html`) en un rol `miweb` con una variable `miweb_carpeta` en `defaults/`. Úsalo desde un playbook de tres líneas.",
  "pista": "Necesitas `roles/miweb/tasks/main.yml` y `roles/miweb/defaults/main.yml`.",
  "solucion": ("yaml", """# roles/miweb/defaults/main.yml
---
miweb_carpeta: /tmp/miweb

# roles/miweb/tasks/main.yml
---
- name: Crear la carpeta
  ansible.builtin.file:
    path: "{{ miweb_carpeta }}"
    state: directory
    mode: "0755"

- name: Crear la página
  ansible.builtin.copy:
    content: "<h1>Hola</h1>"
    dest: "{{ miweb_carpeta }}/index.html"
    mode: "0644"

# site.yml
---
- name: Mi web
  hosts: local
  roles:
    - miweb""")},
 {"titulo": "Cambiar el valor por defecto",
  "enunciado": "Usa el rol anterior pero haz que cree la web en `/tmp/otraweb` sin tocar el rol.",
  "pista": "Cualquier variable del playbook tiene más prioridad que `defaults/`.",
  "solucion": ("yaml", """- name: Mi web en otra carpeta
  hosts: local
  vars:
    miweb_carpeta: /tmp/otraweb
  roles:
    - miweb""")},
]

PROYECTO = {
 "titulo": "Ordena el proyecto en roles",
 "bloques": [
  ("p", "Vas a dividir tu `site.yml` en tres roles. El resultado hace exactamente lo mismo, pero ordenado y reutilizable:"),
  ("table", ["Rol", "Qué hace"], [
   ["`comun`", "Actualiza la lista de paquetes, instala herramientas básicas y pone un mensaje de bienvenida"],
   ["`nginx`", "Instala y configura nginx (con su handler)"],
   ["`web`", "Publica tu web: hoja de estilos, página principal y página de estado"],
  ]),
  ("code", "text", "ansible/", """ansible/
├── ansible.cfg
├── site.yml
├── inventario/
│   ├── hosts.ini
│   └── group_vars/all/web.yml
└── roles/
    ├── comun/
    │   ├── tasks/main.yml
    │   └── templates/motd.j2
    ├── nginx/
    │   ├── defaults/main.yml
    │   ├── handlers/main.yml
    │   ├── tasks/main.yml
    │   └── templates/sitio.conf.j2
    └── web/
        ├── defaults/main.yml
        ├── files/estilo.css
        ├── tasks/main.yml
        └── templates/
            ├── index.html.j2
            └── estado.html.j2"""),
  ("term", """$ cd ansible
$ ansible-galaxy role init roles/comun
$ ansible-galaxy role init roles/nginx
$ ansible-galaxy role init roles/web"""),
  ("p", "Mueve las tareas a cada rol. Así queda el rol `nginx`:"),
  ("code", "yaml", "ansible/roles/nginx/tasks/main.yml", """---
- name: Instalar nginx
  ansible.builtin.apt:
    name: nginx
    state: present

- name: Crear la carpeta de la web
  ansible.builtin.file:
    path: "{{ nginx_raiz }}"
    state: directory
    owner: root
    group: root
    mode: "0755"

- name: Configurar el sitio
  ansible.builtin.template:
    src: sitio.conf.j2
    dest: /etc/nginx/sites-available/miweb
    owner: root
    group: root
    mode: "0644"
  notify: Recargar nginx

- name: Activar el sitio
  ansible.builtin.file:
    src: /etc/nginx/sites-available/miweb
    dest: /etc/nginx/sites-enabled/miweb
    state: link
  notify: Recargar nginx

- name: Desactivar el sitio por defecto
  ansible.builtin.file:
    path: /etc/nginx/sites-enabled/default
    state: absent
  notify: Recargar nginx

- name: Arrancar nginx y activarlo al inicio
  ansible.builtin.service:
    name: nginx
    state: started
    enabled: true"""),
  ("code", "yaml", "ansible/roles/nginx/defaults/main.yml", """---
nginx_raiz: /var/www/miweb"""),
  ("code", "yaml", "ansible/roles/nginx/handlers/main.yml", """---
- name: Recargar nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded"""),
  ("p", "En la plantilla `sitio.conf.j2` cambia `{{ web_raiz }}` por `{{ nginx_raiz }}`. El rol `web` usa su propia variable `web_raiz` con el mismo valor (`/var/www/miweb`) en su `defaults/main.yml`."),
  ("p", "Los archivos completos de los tres roles (incluida una hoja de estilos para que la web se vea bien) están en la carpeta `proyecto/ansible/roles` del repositorio del curso. Cópialos o compáralos con los tuyos."),
  ("p", "El playbook principal queda así de corto:"),
  ("code", "yaml", "ansible/site.yml", """---
- name: Configurar los servidores web
  hosts: web
  become: true
  roles:
    - comun
    - nginx
    - web"""),
  ("term", """$ ansible-playbook site.yml
...
web1 : ok=14  changed=3  unreachable=0  failed=0
web2 : ok=14  changed=3  unreachable=0  failed=0"""),
  ("p", "Resultado de este paso: el mismo resultado de antes, con estilos, y el código ordenado en tres roles reutilizables."),
 ],
}
